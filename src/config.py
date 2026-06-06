import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


class Config:
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    WX_CORP_ID: str = os.getenv("WX_CORP_ID", "")
    WX_AGENT_SECRET: str = os.getenv("WX_AGENT_SECRET", "")
    WX_TOKEN: str = os.getenv("WX_TOKEN", "")
    WX_ENCODING_AES_KEY: str = os.getenv("WX_ENCODING_AES_KEY", "")
    WX_AGENT_ID: str = os.getenv("WX_AGENT_ID", "")

    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'data' / 'association.db'}")
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", str(BASE_DIR / "data" / "chroma"))
    DOCS_DIR: str = os.getenv("DOCS_DIR", str(BASE_DIR / "data" / "docs"))

    MAX_RETRIES: int = 3
    REQUEST_TIMEOUT: int = 60


config = Config()
