import logging
import os

import dotenv
import instructor
import openai

logger = logging.getLogger(__name__)

IS_ENV_EXISTS = os.path.exists(".env")
if IS_ENV_EXISTS:
    logger.info("Loading environment variables from .env file")
    dotenv.load_dotenv(".env")

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_BASE_CLIENT = openai.AsyncOpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
OPENAI_CLIENT = instructor.from_openai(OPENAI_BASE_CLIENT, mode=instructor.Mode.TOOLS_STRICT)
MODEL_LISTS = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
]
