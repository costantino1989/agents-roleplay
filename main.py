import os

# Set global Opik project name before imports to ensure it's picked up by all modules
os.environ["OPIK_PROJECT_NAME"] = "agents-roleplay"

import random
import sys
import argparse
import questionary

from graph import build_graph
from utils.llm_client import Message
from utils.logger import get_logger
from utils.opik_setup import configure_opik
from vector_db.client import GenzeloVectorDB

logger = get_logger("Main")


def main():
    logger.info("--- Initializing HR Onboarding Simulation ---")

    # Initialize Opik
    opik_tracer = configure_opik()

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
    profiles = [
        {
            "name": "Luigi",
            "age": 23,
            "country": "Italy",
            "generation": "genz",
            "job_role": "Junior Software Engineer",
            "language": "Italian"
        },
        {
            "name": "Francesca",
            "age": 45,
            "country": "Italy",
            "generation": "millenials",
            "job_role": "Senior DevOps Engineer",
            "language": "Italian"
        }
    ]

    # 2. Select Profile
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="HR Onboarding Simulation")
    parser.add_argument("--profile", type=str, help="Name of the profile to use (Luigi or Francesca)")
    args = parser.parse_args()

    selected_profile = None

    # Option A: Command Line Argument
    if args.profile:
        selected_profile = next((p for p in profiles if p["name"].lower() == args.profile.lower()), None)
        if not selected_profile:
            logger.error(f"Profile '{args.profile}' not found. Available: {[p['name'] for p in profiles]}")
            sys.exit(1)
        logger.info(f"Profile selected via argument: {selected_profile['name']}")

    # Option B: Interactive Selection (if TTY)
    elif sys.stdin.isatty():
        choices = [
            questionary.Choice(
                title=f"{p['name']} ({p['generation']}, {p['job_role']})",
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
            logger.info(f"Randomly selected profile: {selected_profile['name']}")

    name = selected_profile["name"]
    age = selected_profile["age"]
    country = selected_profile["country"]
    generation = selected_profile["generation"]
    job_role = selected_profile["job_role"]
    language = selected_profile["language"]

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
        "language": language
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
        for event in app.stream(initial_state, {"recursion_limit": 50, "callbacks": [opik_tracer]}):
            for node_name, node_data in event.items():
                if "messages" in node_data:
                    last_msg = node_data["messages"][-1]
                    if isinstance(last_msg, Message):
                        sender_lbl = "HR" if node_name == "hr" else "EMPLOYEE"
                        # Only print content if it has content (not just tool calls) and not from tool
                        if last_msg.content and last_msg.role != "tool":
                            logger.info(f"[{sender_lbl}]: {last_msg.content}")
    except KeyboardInterrupt:
        logger.warning("Simulation stopped by user.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

    logger.info("--- Simulation Completed ---")
    logger.info(f"Profile saved to '{profile_filename}'")


if __name__ == "__main__":
    main()
