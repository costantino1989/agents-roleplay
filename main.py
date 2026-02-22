import os
from utils.custom_model import CustomOpenAICompatibleModel

# Set global Opik project name before imports to ensure it's picked up by all modules
os.environ["OPIK_PROJECT_NAME"] = "agents-roleplay"

import random
import sys
import argparse
import uuid
import questionary

from graph import build_graph
from utils.llm_client import Message
from utils.logger import get_logger
from utils.opik_setup import configure_opik
from vector_db.client import GenzeloVectorDB

from opik.evaluation import evaluate_threads
from opik.evaluation.metrics import ConversationalCoherenceMetric, UserFrustrationMetric

logger = get_logger("Main")


def main():
    logger.info("--- Initializing HR Onboarding Simulation ---")

    # Initialize Opik
    opik_tracer = configure_opik()

    # Generate a unique thread_id for this simulation session
    # This will group all traces of this conversation into a single thread in Opik
    thread_id = str(uuid.uuid4())
    logger.info(f"Session thread_id: {thread_id}")

    # 0. Initialize and Warmup Vector DB
    logger.info("Initializing Vector Knowledge Base...")
    try:
        db_client = GenzeloVectorDB(persist_path=".chroma_db")
        # Warmup search to load model into memory
        db_client.search(query_text="warmup", n_results=1)
        logger.info("Vector Knowledge Base initialized and warmed up.")
    except Exception as e:
        logger.error(f"Failed to initialize Vector DB: {e}")
        sys.exit(1)

    # 1. Define Profiles
    profiles = []
    employee_dir = "employee"
    if os.path.exists(employee_dir):
        import json
        for filename in os.listdir(employee_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(employee_dir, filename), 'r', encoding='utf-8') as f:
                        profiles.append(json.load(f))
                except Exception as e:
                    logger.error(f"Error loading profile from {filename}: {e}")
    else:
        logger.warning(f"Directory '{employee_dir}' not found. No profiles loaded.")

    if not profiles:
        logger.error("No employee profiles found. Please run 'python scripts/build_employee.py' first.")
        sys.exit(1)

    # 2. Select Profile
    parser = argparse.ArgumentParser(description="HR Onboarding Simulation")
    parser.add_argument("--profile", type=str, help="Name of the profile to use (Luigi or Francesca)")
    args = parser.parse_args()

    selected_profile = None

    # Option A: Command Line Argument
    if args.profile:
        selected_profile = next((p for p in profiles if p.get("name", "").lower() == args.profile.lower()), None)
        if not selected_profile:
            logger.error(f"Profile '{args.profile}' not found. Available: {[p.get('name', 'Unknown') for p in profiles]}")
            sys.exit(1)
        logger.info(f"Profile selected via argument: {selected_profile.get('name')}")

    # Option B: Interactive Selection (if TTY)
    elif sys.stdin.isatty():
        choices = [
            questionary.Choice(
                title=f"{p.get('name', 'Unknown')} ({p.get('generation', 'N/A')}, {p.get('job_role', 'N/A')})",
                value=p
            )
            for p in profiles
        ]

        try:
            selected_profile = questionary.select(
                "Choose an employee profile:",
                choices=choices
            ).ask()
        except Exception as e:
            logger.warning(f"Interactive selection failed ({e}). Falling back to random selection.")

    # Option C: Fallback (Non-interactive / Debugger without TTY)
    if not selected_profile:
        if not args.profile and not sys.stdin.isatty():
            logger.warning("No interactive terminal detected. Falling back to random profile.")

        if not selected_profile:
            selected_profile = random.choice(profiles)
            logger.info(f"Randomly selected profile: {selected_profile.get('name', 'Unknown')}")

    name = selected_profile.get("name", "Unknown")
    age = selected_profile.get("age", "Unknown")
    country = selected_profile.get("country", "Unknown")
    generation = selected_profile.get("generation", "Unknown")
    job_role = selected_profile.get("job_role", "Unknown")
    language = selected_profile.get("language", "English")
    employee_prompt = selected_profile.get("prompt", "")

    logger.info(
        f"Starting Simulation for: {name} ({age}, {country}, {generation}) | Job: {job_role} | Agents language: {language}")

    # 3. Initialize State
    initial_state = {
        "messages": [],
        "hr_messages": [],
        "employee_messages": [],
        "name": name,
        "hr_name": "Alex",
        "age": age,
        "country": country,
        "generation": generation,
        "job_role": job_role,
        "sender": "system",
        "language": language,
        "employee_prompt": employee_prompt
    }

    # 4. Run Graph
    app = build_graph(db_client)

    # Initialize profile file
    profile_filename = f"{name}_profile.md"
    try:
        with open(profile_filename, "w") as f:
            f.write(f"# Employee Profile: {name}\n\n")
    except Exception as e:
        logger.error(f"Failed to create profile file: {e}")

    try:
        for event in app.stream(
            initial_state,
            {
                "recursion_limit": 50,
                "callbacks": [opik_tracer], # [opik_tracer] Disabled due to Pydantic/Opik compatibility issue
                # LangGraph reads thread_id from "configurable" — Opik picks this up
                # automatically to group all traces of this session into a single thread
                "configurable": {"thread_id": thread_id}
            }
        ):
            for node_name, node_data in event.items():
                if "messages" in node_data:
                    last_msg = node_data["messages"][-1]
                    if isinstance(last_msg, Message):
                        sender_lbl = "HR" if node_name == "hr" else "EMPLOYEE"
                        if last_msg.content and last_msg.role != "tool":
                            logger.info(f"[{sender_lbl}]: {last_msg.content}")
    except KeyboardInterrupt:
        logger.warning("Simulation stopped by user.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

    logger.info("--- Simulation Completed ---")
    logger.info(f"Profile saved to '{profile_filename}'")

    # 5. Evaluate the conversation thread just completed
    logger.info("--- Running Thread Evaluation ---")
    try:
        # Flush all pending traces to Opik before evaluating
        opik_tracer.flush()
        logger.info("Traces flushed to Opik.")

        # Close the thread via the REST client so it becomes "inactive"
        # evaluate_threads only processes inactive threads
        import opik as opik_sdk
        opik_client = opik_sdk.Opik(project_name="agents-roleplay")
        opik_client.rest_client.traces.close_trace_thread(
            thread_id=thread_id,
            project_name="agents-roleplay"
        )
        logger.info(f"Thread '{thread_id}' marked as inactive.")

        custom_model = CustomOpenAICompatibleModel(
            model_name=os.getenv("OPENROUTER_MODEL_NAME"),
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url=os.getenv("OPENROUTER_BASE_URL")
        )
        results = evaluate_threads(
            project_name="agents-roleplay",
            filter_string=f'id = "{thread_id}"',
            eval_project_name="agents-roleplay-evaluation",
            metrics=[
                ConversationalCoherenceMetric(model=custom_model, window_size=40, temperature=0.8),
                UserFrustrationMetric(model=custom_model, window_size=40, temperature=0.8),
            ],
            trace_input_transform=lambda x: x.get("input", ""),
            trace_output_transform=lambda x: x.get("output", ""),
        )
        logger.info(f"Evaluation complete. Results: {results}")
    except Exception as e:
        logger.error(f"Thread evaluation failed: {e}")


if __name__ == "__main__":
    main()