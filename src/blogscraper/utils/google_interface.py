from pathlib import Path
from typing import Any

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from blogscraper.utils.sys_utils import find_project_root, get_env_secret


def get_service_account_path() -> Path:
    service_account_file = get_env_secret("GOOGLE_SERVICE_ACCOUNT_FILE")
    if not service_account_file:
        raise ValueError("GOOGLE_SERVICE_ACCOUNT_FILE is not set in .env.secret")
    path = find_project_root() / service_account_file

    if not path.exists():
        raise FileNotFoundError(f"Service account file not found: {path}")

    return path


def get_services() -> Any:
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
    document = DOCS_SERVICE.documents().create(body={"title": title}).execute()
    doc_id = document["documentId"]
    permission = {"type": "anyone", "role": "reader"}
    DRIVE_SERVICE.permissions().create(fileId=doc_id, body=permission).execute()
    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
    return doc_id, doc_url


def write_to_google_doc(doc_id: str, text: str) -> None:
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
