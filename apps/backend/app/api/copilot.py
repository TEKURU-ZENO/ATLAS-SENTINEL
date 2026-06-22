from fastapi import APIRouter

router = APIRouter()


@router.get("/ask")
def ask(question: str = "Can I start welding in Zone C?") -> dict:
    return {
        "question": question,
        "answer": "Unsafe. Methane exceeds safe hot work conditions in Zone C. Suspend PTW-4421.",
        "citations": ["Methane Sensor C-04", "Permit PTW-4421", "OISD hot work control"],
    }
