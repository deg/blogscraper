from blogscraper.types import GDoc
from blogscraper.ui import confirm_action, select_google_docs
from blogscraper.utils.google_interface import (
    delete_service_account_doc,
    list_service_account_docs,
)


def delete_unneeded_docs() -> None:
    all_old_google_docs = list_service_account_docs()
    if all_old_google_docs and confirm_action("Delete some old Google Docs?"):
        handle_google_doc_cleanup(all_old_google_docs)


def handle_google_doc_cleanup(old_docs: list[GDoc]) -> None:
    """Deletes selected old Google Docs."""
    doc_ids_to_delete = select_google_docs(old_docs, "delete")
    for doc in doc_ids_to_delete:
        delete_service_account_doc(doc.id, doc.name)
