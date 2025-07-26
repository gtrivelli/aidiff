import os
from dotenv import load_dotenv

# Config and environment variable handling

load_dotenv()

def get_openai_api_key():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY not found. Please set it in your .env file or environment variables.")
    return key

def get_gemini_api_key():
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY not found. Please set it in your .env file or environment variables.")
    return key
