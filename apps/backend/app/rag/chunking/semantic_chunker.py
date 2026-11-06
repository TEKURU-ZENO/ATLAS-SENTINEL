import re


HEADING = re.compile(r"(?m)^\s*((?:CHAPTER|PART|SECTION)\s+[IVXLC0-9A-Z.-]+[^\n]*|\d+(?:\.\d+)*[A-Z]?(?:\s*[-–—.:]\s*|\s+)[A-Z][^\n]{3,160})\s*$", re.I)


def chunk_text(text: str, size: int = 1100, overlap: int = 160) -> list[dict]:
    """Chunk on legal headings/paragraphs while retaining a heading for citations."""
    text = re.sub(r"[ \t]+", " ", text.replace("\r", ""))
    sections = []
    matches = list(HEADING.finditer(text))
    if matches:
        for index, match in enumerate(matches):
            stop = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            sections.append((match.group(1).strip(), text[match.start():stop].strip()))
    else:
        sections = [("", text)]
    chunks = []
    for heading, body in sections:
        if not body:
            continue
        start = 0
        while start < len(body):
            stop = min(len(body), start + size)
            if stop < len(body):
                boundary = max(body.rfind("\n\n", start, stop), body.rfind(". ", start, stop))
                if boundary > start + size // 2:
                    stop = boundary + (2 if body[boundary:boundary + 2] == ". " else 0)
            part = body[start:stop].strip()
            if part:
                chunks.append({"heading": heading, "text": part})
            if stop >= len(body):
                break
            start = max(start + 1, stop - overlap)
    return chunks
