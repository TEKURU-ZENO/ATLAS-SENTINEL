def chunk_text(text: str, size: int = 600) -> list[str]:
    return [text[index:index + size] for index in range(0, len(text), size)]
