from pydantic import BaseModel
from fastapi import APIRouter
from app.services.rag import (answer_question)

router = APIRouter()

class ChatRequest(BaseModel):
    question: str

@router.post("/chat")
def chat(request: ChatRequest):
    answer = answer_question(
        request.question
    )

    return {
        "answer": answer
    }