import os
from pathlib import Path

from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build


def find_project_root(start_path: Path) -> Path:
    for parent in start_path.resolve().parents:
        if (parent / "Makefile").exists():
            return parent
    raise FileNotFoundError("Could not find project root")


PROJECT_ROOT = find_project_root(Path(__file__))
ENV_SECRET_PATH = PROJECT_ROOT / ".env.secret"

if not ENV_SECRET_PATH.exists():
    raise FileNotFoundError(f"Missing .env.secret file at {ENV_SECRET_PATH}")

load_dotenv(ENV_SECRET_PATH)

SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
if not SERVICE_ACCOUNT_FILE:
    raise ValueError("GOOGLE_SERVICE_ACCOUNT_FILE is not set in .env.secret")

SERVICE_ACCOUNT_FILE_PATH = PROJECT_ROOT / SERVICE_ACCOUNT_FILE

if not SERVICE_ACCOUNT_FILE_PATH.exists():
    raise FileNotFoundError(
        f"Service account file not found: {SERVICE_ACCOUNT_FILE_PATH}"
    )

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
]

# Authenticate and build the service clients
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
drive_service = build("drive", "v3", credentials=credentials)
docs_service = build("docs", "v1", credentials=credentials)

print(f"SERVICES:\n\n{drive_service}\n\n{docs_service}")

# Step 1: Create a new Google Doc
document = docs_service.documents().create(body={"title": "My New Document"}).execute()
doc_id = document["documentId"]
print(f"Created Document ID: {doc_id}")

# Step 2: Add text to the Google Doc
requests = [
    {
        "insertText": {
            "location": {"index": 1},
            "text": "Hello, this is a test document.\n",
        }
    }
]
docs_service.documents().batchUpdate(
    documentId=doc_id, body={"requests": requests}
).execute()

# Step 3: Make the document publicly viewable
permission = {"type": "anyone", "role": "reader"}
drive_service.permissions().create(fileId=doc_id, body=permission).execute()

# Step 4: Get the URL of the document
doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
print(f"Document URL: {doc_url}")
