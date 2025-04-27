from dotenv import load_dotenv
import os

def load_env():
    load_dotenv()
    return {
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
    }