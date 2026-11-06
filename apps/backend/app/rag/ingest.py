import argparse
import hashlib
import json
from pathlib import Path

from app.rag.chunking.semantic_chunker import chunk_text
from app.rag.loaders.pdf_loader import load_pdf
from app.rag.vectorstore.sqlite_store import SQLiteDocumentStore


def ingest(path: Path, store: SQLiteDocumentStore | None = None) -> dict:
    if not path.exists():
        raise FileNotFoundError(path)
    store = store or SQLiteDocumentStore()
    files = [path] if path.is_file() else sorted(path.rglob("*"))
    indexed = 0
    skipped = []
    for file in files:
        if not file.is_file() or file.suffix.lower() not in {".pdf", ".txt", ".md"}:
            continue
        historical = "factories_act" in file.stem.lower() or "factories act" in file.stem.lower()
        pages = load_pdf(str(file)) if file.suffix.lower() == ".pdf" else [{"text": file.read_text(encoding="utf-8"), "page": None, "section": ""}]
        for page in pages:
            for number, chunk in enumerate(chunk_text(page["text"])):
                citation = {
                    "document": f"Historical: {file.name}" if historical else file.name,
                    "section": chunk["heading"] or page.get("section", ""),
                    "page": page.get("page"),
                    "legal_status": "historical; Factories Act repealed from 2025-11-21" if historical else "source copy; verify current status",
                    "source_path": str(file),
                }
                fingerprint = hashlib.sha256((str(file.resolve()) + str(page.get("page")) + str(number) + chunk["text"]).encode()).hexdigest()[:20]
                store.upsert(f"file-{fingerprint}", chunk["text"], citation)
                indexed += 1
        if not pages:
            skipped.append(file.name)
    return {"indexed_chunks": indexed, "skipped": skipped, "total_documents": store.count()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Index local regulation PDFs or text files with page/section citations.")
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    print(json.dumps(ingest(args.path), indent=2))
