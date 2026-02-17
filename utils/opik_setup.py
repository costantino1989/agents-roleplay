import opik
import os
from opik.integrations.langchain import OpikTracer
# Import prompts
from prompts.francesca_prompt import FRANCESCA_SYSTEM_PROMPT
from prompts.hr_agent_prompt import HR_SYSTEM_PROMPT
from prompts.kb_prompt import KB_PROMPT
from prompts.luigi_prompt import LUIGI_SYSTEM_PROMPT
from utils.logger import get_logger

logger = get_logger("OpikSetup")


def configure_opik(project_name="agents-roleplay"):
    """
    Initializes Opik, syncs prompts, and returns the tracer.
    """
    logger.info(f"Initializing Opik for project: {project_name}")
    
    # Set global environment variable to ensure all threads/processes use this project
    os.environ["OPIK_PROJECT_NAME"] = project_name

    # Initialize Client
    client = opik.Opik(project_name=project_name)

    # Sync Prompts
    prompts_to_sync = {
        "Francesca System Prompt": FRANCESCA_SYSTEM_PROMPT,
        "HR System Prompt": HR_SYSTEM_PROMPT,
        "KB Extraction Prompt": KB_PROMPT,
        "Luigi System Prompt": LUIGI_SYSTEM_PROMPT
    }

    for name, content in prompts_to_sync.items():
        try:
            # Check if prompt exists or create/update it
            # Opik's create_prompt usually creates a new version if it exists
            client.create_prompt(name=name, prompt=content)
            logger.info(f"Synced prompt: {name}")
        except Exception as e:
            logger.error(f"Failed to sync prompt {name}: {e}")

    return OpikTracer(project_name="agents-roleplay", tags=["judge", "judge-role-play"])
