import logging
from fastapi import APIRouter, Depends, HTTPException

from app.schemas.chat_schema import ChatRequest, ChatResponse, SearchRequest
from app.services.search_products import search_products
from app.services.agent_router import handle_chat_routing

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # 1. Call the Guardrails + LLM logic
        result = await handle_chat_routing(request.user_input)
        logger.debug(f"Chat response: {result}")
        # Extract the text content
        raw_content = result["content"]
        
        # If raw_content is a dict (from NeMo), get the "content" key
        if isinstance(raw_content, dict):
            final_text = raw_content.get("content", "")
        else:
            final_text = str(raw_content)

        return ChatResponse(
            response=final_text,
            tool=result.get("tool", "none"),
            source="guarded_llm"
        )
    except Exception as e:
        logger.error(f"Error in chat_endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


@router.post("/api/v1/search")
async def search_endpoint(request: SearchRequest):
    product = await search_products(request.user_input)
    
    if product is None:
        # This prevents the ResponseValidationError by stopping the flow
        # and returning a proper 404 error to the client.
        raise HTTPException(
            status_code=404, 
            detail="No product found matching that description."
        )
    
    return product
        