import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
REDIS_URL = os.getenv("REDIS_URL", "").strip()
USE_CHROMA = os.getenv("USE_CHROMA", "true").lower() in ("1", "true", "yes")
CHROMA_PATH = os.getenv("CHROMA_PATH", str(DATA_DIR / "chroma_db"))
