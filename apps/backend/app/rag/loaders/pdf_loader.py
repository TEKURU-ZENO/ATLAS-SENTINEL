import re
from pathlib import Path

from pypdf import PdfReader


SECTION = re.compile(r"(?im)^\s*((?:section\s+)?\d+[A-Z]?(?:\.\d+)*\.?\s+[A-Z][^\n]{4,140})\s*$")


def load_pdf(path: str) -> list[dict]:
    source = Path(path)
    reader = PdfReader(str(source))
    current_section = ""
    pages = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        headings = SECTION.findall(text)
        if headings:
            current_section = headings[-1].strip()
        if text:
            pages.append({"text": text, "page": page_number, "section": current_section, "source": source.name})
    return pages
