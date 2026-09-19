import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def database_path() -> Path:
    """Resolve relative overrides against the project, never the working directory."""
    path = Path(os.environ.get("LIFEDESK_DB_PATH", "data/lifedesk.db"))
    return (PROJECT_ROOT / path).resolve()
