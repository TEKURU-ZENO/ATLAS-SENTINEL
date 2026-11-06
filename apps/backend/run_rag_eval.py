import json
import sys
from pathlib import Path


BACKEND = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND))

from app.rag.evaluate import evaluate  # noqa: E402


print(json.dumps(evaluate(), indent=2))
