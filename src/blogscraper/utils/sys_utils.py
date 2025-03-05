import os
from pathlib import Path

from dotenv import load_dotenv

# Name of a file that is certain to exist in the project root directory
A_FILE_IN_ROOT_DIR = "Makefile"


def find_project_root(start_path: Path = Path(__file__)) -> Path:
    for parent in start_path.resolve().parents:
        if (parent / A_FILE_IN_ROOT_DIR).exists():
            return parent
    raise FileNotFoundError("Could not find project root")


def get_env_secret(key: str) -> str | None:
    project_root = find_project_root()
    env_secret_path = project_root / ".env.secret"
    if not env_secret_path.exists():
        raise FileNotFoundError(f"Missing .env.secret file at {env_secret_path}")
    load_dotenv(env_secret_path)
    return os.getenv(key)
