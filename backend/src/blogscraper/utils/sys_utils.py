"""System utility functions for locating the project root and loading secrets.

Provides helper functions to determine the project's root directory based on the
existence of known files and to safely load environment secrets from `.env.secret`.

Environment Variables:
    - Secrets are expected to be stored in `<ROOT>/.env.secret`, which should never
      be committed to version control.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Name of a file that is certain to exist in the project root directory
A_FILE_IN_ROOT_DIR = "Makefile"


def find_project_root(start_path: Path = Path(__file__)) -> Path:
    """Finds the root directory of the project by locating a known file.

    Args:
        start_path (Path, optional): The starting path for the search. Defaults to the
        location of this file.

    Returns:
        Path: The absolute path to the project root directory.

    Raises:
        FileNotFoundError: If the root directory cannot be determined.
    """
    for parent in start_path.resolve().parents:
        if (parent / A_FILE_IN_ROOT_DIR).exists():
            return parent
    raise FileNotFoundError("Could not find project root")


def get_env_secret(key: str) -> str | None:
    """Retrieves a secret value from the `.env.secret` file.

    Args:
        key (str): The name of the environment variable to retrieve.

    Returns:
        str | None: The value of the requested secret, or None if not found.

    Raises:
        FileNotFoundError: If the `.env.secret` file is missing.
    """
    project_root = find_project_root()
    env_secret_path = project_root / ".env.secret"
    if not env_secret_path.exists():
        raise FileNotFoundError(f"Missing .env.secret file at {env_secret_path}")
    load_dotenv(env_secret_path)
    return os.getenv(key)
