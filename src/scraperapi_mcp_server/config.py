from dotenv import load_dotenv
from pydantic_settings import BaseSettings


load_dotenv()


class ApiKeyEnvVarNotSetError(Exception):
    """Raised when the API key environment variable is not set."""

    pass


class Settings(BaseSettings):
    """ScraperAPI MCP Server settings."""

    API_KEY: str = ""
    API_URL: str = "https://api.scraperapi.com"
    API_TIMEOUT_SECONDS: int = 70
    RATE_LIMIT_MAX_CALLS: int = 10
    RATE_LIMIT_WINDOW_SECONDS: float = 60.0
    IMAGE_SIZE_LIMIT_BYTES: int = (
        700_000  # ~700KB raw → ~933KB base64, stays under 1MB transport limit
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.API_KEY:
            raise ApiKeyEnvVarNotSetError(
                "API_KEY environment variable is not set. Please set it when installing the MCP server. Check the README for more information."
            )


settings = Settings()
