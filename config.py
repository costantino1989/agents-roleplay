import os
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = os.getenv("MODEL_NAME", "mistral-small-latest")

# Evaluation Configuration
EVAL_MODEL_NAME = os.getenv("EVAL_MODEL_NAME")
EVAL_BASE_URL = os.getenv("EVAL_BASE_URL")
EVAL_API_KEY = os.getenv("EVAL_API_KEY")
