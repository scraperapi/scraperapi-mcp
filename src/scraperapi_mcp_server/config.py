import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings


load_dotenv()


class Settings(BaseSettings):
    """ScraperAPI MCP Server settings."""

    API_KEY: str = os.getenv("API_KEY", "")
    API_URL: str = "https://api.scraperapi.com"
    API_TIMEOUT_SECONDS: int = 70
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.API_KEY:
            raise ValueError("API_KEY environment variable is not set. Please set it when installing the MCP server. Check the README for more information.")

settings = Settings()