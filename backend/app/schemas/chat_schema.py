from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    user_input: str
    session_id: str = "default_session"

class ChatResponse(BaseModel):
    response: str
    source: str 
    tool: str = "none"

class SearchRequest(BaseModel):
    # The 'user_input' field is what the client sends
    user_input: str = Field(
        ..., 
        description="The product description or query from the client",
        example="I'm looking for a high-pressure industrial pump"
    )