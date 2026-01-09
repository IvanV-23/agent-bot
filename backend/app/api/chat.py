import logging
from fastapi import APIRouter, Depends, HTTPException

from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.services.guardrails import get_chat_response


logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # 1. Call the Guardrails + LLM logic
        result = await get_chat_response(request.user_input)
        
        # 2. Extract content from the NeMo response format
        return ChatResponse(
            response=result["content"],
            source="guarded_llm"
        )
    except Exception as e:
        logger.error(f"Error in chat_endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")
