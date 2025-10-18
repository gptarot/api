import logging
import os

import dotenv
import openai

logger = logging.getLogger(__name__)

IS_ENV_EXISTS = os.path.exists(".env")
if IS_ENV_EXISTS:
    logger.info("Loading environment variables from .env file")
    dotenv.load_dotenv(".env")

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_CLIENT = openai.AsyncOpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
