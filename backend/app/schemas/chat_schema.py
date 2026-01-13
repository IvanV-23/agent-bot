from pydantic import BaseModel

class ChatRequest(BaseModel):
    user_input: str
    session_id: str = "default_session"

class ChatResponse(BaseModel):
    response: str
    source: str 
    tool: str = "none"
