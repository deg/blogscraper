"""Provides an interface to interact with Google Drive and Google Docs using
Google API services. Handles authentication via a service account and
provides methods to create and modify documents.

Environment Variables:
    - GOOGLE_SERVICE_ACCOUNT_FILE: Path to the service account JSON credentials. Loaded
from <ROOT>/.env.secret, which should never be committed to git.

---

For setup instructions, including enabling APIs, creating a service account, and
configuring credentials, refer to <ROOT>/dev-docs/google-integration.md in the project
root.

Key steps:
- Enable Google Drive & Docs API in Google Cloud Console.
- Create a service account with necessary permissions.
- Generate a JSON key and store it securely in <ROOT>/secrets/.
- Add `GOOGLE_SERVICE_ACCOUNT_FILE=secrets/<YOUR_KEY>.json` to <ROOT>/.env.secret.

"""

from pathlib import Path
from typing import Any

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from blogscraper.utils.sys_utils import find_project_root, get_env_secret


def get_service_account_path() -> Path:
    """Retrieves the path to the Google service account JSON credentials file.

    Returns:
        Path: The full path to the service account file.

    Raises:
        ValueError: If GOOGLE_SERVICE_ACCOUNT_FILE is not set in the environment.
        FileNotFoundError: If the specified service account file does not exist.
    """
    service_account_file = get_env_secret("GOOGLE_SERVICE_ACCOUNT_FILE")
    if not service_account_file:
        raise ValueError("GOOGLE_SERVICE_ACCOUNT_FILE is not set in .env.secret")
    path = find_project_root() / service_account_file

    if not path.exists():
        raise FileNotFoundError(f"Service account file not found: {path}")

    return path


def get_services() -> Any:
    """Initializes and returns Google Drive and Google Docs API service clients.

    Returns:
        tuple[Any, Any]: A tuple containing Drive and Docs service clients.
    """
    scopes = [
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/documents",
    ]
    creds = Credentials.from_service_account_file(  # type: ignore[no-untyped-call]
        str(get_service_account_path()), scopes=scopes
    )
    return (
        build("drive", "v3", credentials=creds),
        build("docs", "v1", credentials=creds),
    )


DRIVE_SERVICE, DOCS_SERVICE = get_services()


def create_google_doc(title: str) -> tuple[str, str]:
    """Creates a new Google Document with the given title and returns its ID and URL.

    Args:
        title (str): The title of the new Google Document.

    Returns:
        tuple[str, str]: A tuple containing the document ID and its shareable URL.
    """
    document = DOCS_SERVICE.documents().create(body={"title": title}).execute()
    doc_id = document["documentId"]
    permission = {"type": "anyone", "role": "reader"}
    DRIVE_SERVICE.permissions().create(fileId=doc_id, body=permission).execute()
    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
    return doc_id, doc_url


def write_to_google_doc(doc_id: str, text: str) -> None:
    """Writes text to an existing Google Document.

    Args:
        doc_id (str): The ID of the Google Document.
        text (str): The text content to be inserted into the document.
    """
    requests = [
        {
            "insertText": {
                "location": {"index": 1},
                "text": text,
            }
        }
    ]
    DOCS_SERVICE.documents().batchUpdate(
        documentId=doc_id, body={"requests": requests}
    ).execute()
