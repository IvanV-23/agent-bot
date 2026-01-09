from fastapi import APIRouter, Depends, HTTPException
from app.schemas.chat_schema import ChatRequest, ChatResponse


router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        
        result = {
            "content": "This is a simulated response.",
            "source": "llm"
        }

        return ChatResponse(
            response=result["content"],
            source=result.get("source", "llm")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
