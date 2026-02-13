# GenZ & Millennials HR Onboarding POC - Project Context

## Project Overview

This project aims to build an **intelligent HR Onboarding Agent** that simulates a conversation between an HR representative and a new employee. The core feature is its ability to adapt to **Gen Z and Millennial** personalities using a retrieved Knowledge Base (KB) of generational insights.

**Current Status:** The project is currently in the **Data Extraction & Knowledge Base Creation** phase. The core application logic (agents, retrieval tools) described in the main `README.md` is planned but not yet fully implemented in the root directory.

## Architecture & Workflow

### 1. Data Pipeline (Active)
The immediate focus is on generating a structured Knowledge Base from raw survey data.

*   **Source:** `SimBench` dataset (via HuggingFace).
*   **Processing:** `extraction_and_create_kb.ipynb`
    *   Loads the dataset.
    *   Filters for **European countries**.
    *   Classifies respondents into **Gen Z** or **Millennials**.
    *   Uses an LLM (via `openai`) with a specialized prompt (`prompts/kb_prompt.py`) to extract behavioral patterns.
*   **Output:** JSON files in `data/` (e.g., `genz.json`, `millenials.json`).

### 2. Runtime Application (Target/Planned)
As described in `README.md`, the target application will consist of:
*   **HR Agent:** Generates questions based on retrieved insights.
*   **Retrieval Node:** Semantic search over the generated JSON KB.
*   **Employee Agent:** Simulates responses based on generational persona.
*   **Profile Manager:** Extracts and saves user profile data.

## Key Files

*   **`extraction_and_create_kb.ipynb`**: The main notebook for data analysis, filtering, and running the LLM extraction pipeline.
*   **`prompts/kb_prompt.py`**: Contains `KB_PROMPT`, the system instruction used to extract "concrete behavioral patterns" from survey questions.
*   **`data/`**: Directory containing the generated Knowledge Bases (`genz.json`, `millenials.json`).
*   **`pyproject.toml`**: Project configuration and dependencies (managed by `uv`).
*   **`main.py`**: Current entry point placeholder.
*   **`README.md`**: Describes the **target** final application features and usage.

## Setup & Development

### Dependency Management
This project uses **uv** for dependency management.

```bash
# Sync dependencies
uv sync
```

### Running the Data Pipeline
To regenerate or analyze the knowledge base, run the Jupyter Notebook:

```bash
# Activate virtual environment (if needed)
source .venv/bin/activate

# Start Jupyter
jupyter lab extraction_and_create_kb.ipynb
```

### Important Notes
*   **LLM Provider:** The `pyproject.toml` includes `openai`, suggesting the data extraction pipeline uses OpenAI models. However, the `README.md` mentions `Anthropic` and `Claude Sonnet` for the agent runtime. Be aware of this potential hybrid approach or migration.
*   **Missing Files:** Files mentioned in `README.md` like `genz_retrieval_tool.py` or `langgraph_hr_with_profile_saving.py` are currently not in the root. They may be created later or are part of a refactor in progress.

## Development Conventions
*   **Data-Driven:** The core logic relies on the quality of the `data/*.json` files. Verify these exist and are populated before working on the runtime agents.
*   **Prompt Engineering:** Modifications to how insights are extracted should be made in `prompts/kb_prompt.py`.
