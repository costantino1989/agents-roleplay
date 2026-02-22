import json
import os
import re
import sys
from collections import Counter
from typing import List, Dict, Any

import questionary
from openai import OpenAI
from dotenv import load_dotenv

# Ensure the project root is in the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from prompts.employee_builder_prompt import EMPLOYEE_BUILDER_SYSTEM_PROMPT, EMPLOYEE_BUILDER_USER_PROMPT

# Load environment variables
load_dotenv()

def main():
    # 1. Select Generation
    generation = questionary.select(
        "Select generation:",
        choices=["genz", "millenials"]
    ).ask()

    if not generation:
        print("No generation selected. Exiting.")
        return

    # 1.5 Select Job Role
    job_roles = [
        "Software Developer",
        "Data Engineer",
        "Cloud Architect",
        "DevOps Engineer",
        "Frontend Developer",
        "Backend Developer",
        "Full Stack Developer",
        "Data Scientist",
        "UX/UI Designer",
        "Product Owner",
        "Scrum Master",
        "Cybersecurity Analyst",
        "Other"
    ]
    
    job_role = questionary.select(
        "Select job role at TechVision Consulting:",
        choices=job_roles
    ).ask()

    if job_role == "Other":
        job_role = questionary.text("Enter custom job role:").ask()

    if not job_role:
        print("No job role selected. Exiting.")
        return

    # 1.6 Select Country
    country = questionary.text("Enter country (e.g., Italy, Germany, France):", default="Italy").ask()

    # 1.7 Select Language
    language = questionary.text("Enter language (e.g., Italian, English, French):", default="Italian").ask()

    # 2. Load Dataset
    data_file = f"data/{generation}.json"
    if not os.path.exists(data_file):
        print(f"Error: Data file {data_file} not found.")
        return

    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 3. Extract Metadata and Count
    all_metadata = []
    for entry in data:
        if "metadata" in entry and isinstance(entry["metadata"], list):
            all_metadata.extend(entry["metadata"])
    
    metadata_counts = Counter(all_metadata)

    # 4. Show Metadata and Request Input
    # Sort metadata by count (descending) for better UX
    sorted_metadata = sorted(metadata_counts.items(), key=lambda x: x[1], reverse=True)
    
    choices = [
        questionary.Choice(title=f"{tag} ({count})", value=tag)
        for tag, count in sorted_metadata
    ]

    selected_metadata = questionary.checkbox(
        "Select metadata to generate the prompt (Space to select, Enter to confirm):",
        choices=choices
    ).ask()

    if not selected_metadata:
        print("No metadata selected. Exiting.")
        return

    print(f"\nSelected metadata: {selected_metadata}")

    # 5. Filter Documents
    filtered_docs = []
    for entry in data:
        entry_metadata = set(entry.get("metadata", []))
        # Check if there is any intersection between selected metadata and entry metadata
        if not set(selected_metadata).isdisjoint(entry_metadata):
            filtered_docs.append(entry["doc"])

    if not filtered_docs:
        print("No documents found matching the selected metadata.")
        return

    print(f"Found {len(filtered_docs)} documents matching the criteria.")
    
    # Prepare documents string for prompt
    documents_str = "\n\n".join([f"- {doc}" for doc in filtered_docs])

    # 6. Call OpenAI Client
    client = OpenAI(
        base_url=os.getenv("OPENROUTER_BASE_URL"),
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )

    model = os.getenv("CLAUDE_MODEL_NAME", "gpt-4o") # Default fallback if env var not set

    print(f"\nGenerating prompt using model: {model}...")

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": EMPLOYEE_BUILDER_SYSTEM_PROMPT},
                {"role": "user", "content": EMPLOYEE_BUILDER_USER_PROMPT.format(
                    generation=generation,
                    job_role=job_role,
                    country=country,
                    language=language,
                    selected_metadata=", ".join(selected_metadata),
                    documents=documents_str
                )}
            ],
            temperature=0.8
        )
        
        generated_prompt = response.choices[0].message.content
        
        print("\n" + "="*50)
        print("GENERATED EMPLOYEE PROMPT")
        print("="*50 + "\n")
        print(generated_prompt)
        print("\n" + "="*50)

        # Save to JSON file
        # Extract name using regex (try "You are [Name]" or "Name: [Name]")
        name_match = re.search(r"You are ([A-Z][a-z]+)", generated_prompt) or re.search(r"Name:\s*([A-Z][a-z]+)", generated_prompt)
        employee_name = name_match.group(1) if name_match else "Unknown"

        if employee_name == "Unknown":
             print("Warning: Could not extract employee name from prompt. Using default filename.")
             output_filename_base = "employee_prompt"
        else:
             output_filename_base = employee_name

        # Extract age using regex
        age_match = re.search(r"(\d{2})-year-old", generated_prompt) or re.search(r"Age:\s*(\d{2})", generated_prompt)
        employee_age = int(age_match.group(1)) if age_match else "Unknown"

        # Save to JSON file in employee/ directory
        output_dir = "employee"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        output_filename = os.path.join(output_dir, f"{output_filename_base}.json")
        
        output_data = {
            "name": employee_name,
            "age": employee_age,
            "country": country,
            "generation": generation,
            "job_role": job_role,
            "language": language,
            "prompt": generated_prompt
        }

        try:
            with open(output_filename, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=4, ensure_ascii=False)
            print(f"\nPrompt successfully saved to '{output_filename}'.")
        except IOError as e:
            print(f"\nError saving prompt to file: {e}")

    except Exception as e:
        print(f"Error calling OpenAI API: {e}")

if __name__ == "__main__":
    main()
