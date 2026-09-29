import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Central configuration loaded from environment variables."""
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    ADMIN_API_URL: str = os.getenv("ADMIN_API_URL", "http://localhost:8001")
    ADMIN_API_KEY: str = os.getenv("ADMIN_API_KEY", "secret-admin-key")


settings = Settings()
