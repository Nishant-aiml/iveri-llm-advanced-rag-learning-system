"""Content library — subject-based document storage and pre-indexed content."""
import json
import logging
from pathlib import Path
from app.config import STORAGE_DIR

logger = logging.getLogger(__name__)

LIBRARY_DIR = STORAGE_DIR / "library"
LIBRARY_DIR.mkdir(parents=True, exist_ok=True)

# In-memory catalog: {subject: [doc_id, ...]}
_catalog: dict[str, list[str]] = {}


def _load_catalog():
    """Load library catalog from disk."""
    global _catalog
    catalog_path = LIBRARY_DIR / "catalog.json"
    if catalog_path.exists():
        with open(catalog_path, "r", encoding="utf-8") as f:
            _catalog = json.load(f)
        logger.info(f"Loaded library catalog: {len(_catalog)} subjects")
    else:
        _catalog = {}


def _save_catalog():
    """Save library catalog to disk."""
    catalog_path = LIBRARY_DIR / "catalog.json"
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump(_catalog, f, ensure_ascii=False, indent=2)


def add_to_library(doc_id: str, subject: str, title: str = ""):
    """Add a processed document to the content library under a subject."""
    if subject not in _catalog:
        _catalog[subject] = []

    entry = {"doc_id": doc_id, "title": title}
    # Avoid duplicates
    existing_ids = [e["doc_id"] if isinstance(e, dict) else e for e in _catalog[subject]]
    if doc_id not in existing_ids:
        _catalog[subject].append(entry)
        _save_catalog()
        logger.info(f"Added doc {doc_id} to library under '{subject}'")


def get_subjects() -> list[dict]:
    """Get all subjects and their document counts."""
    return [
        {"subject": subj, "doc_count": len(docs)}
        for subj, docs in _catalog.items()
    ]


def get_subject_docs(subject: str) -> list[dict]:
    """Get all documents in a subject."""
    docs = _catalog.get(subject, [])
    return [d if isinstance(d, dict) else {"doc_id": d, "title": ""} for d in docs]


def remove_from_library(doc_id: str, subject: str = None):
    """Remove a document from the library."""
    if subject:
        if subject in _catalog:
            _catalog[subject] = [
                d for d in _catalog[subject]
                if (d.get("doc_id") if isinstance(d, dict) else d) != doc_id
            ]
            _save_catalog()
    else:
        # Remove from all subjects
        for subj in _catalog:
            _catalog[subj] = [
                d for d in _catalog[subj]
                if (d.get("doc_id") if isinstance(d, dict) else d) != doc_id
            ]
        _save_catalog()


# Load catalog on module import
_load_catalog()
