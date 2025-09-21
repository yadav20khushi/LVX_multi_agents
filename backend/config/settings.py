from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

class Settings(BaseSettings):

    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    GOOGLE_GENAI_USE_VERTEXAI: bool = os.getenv("GOOGLE_GENAI_USE_VERTEXAI")
    MODEL_ID: str = os.getenv("gemini-2.5-flash")


settings = Settings()

