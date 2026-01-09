from fastapi import FastAPI
from app.api.chat import router as chat_router



app = FastAPI(
    title="Ivabot",
    version="1.0.0"
)

# 2. Include API routes
app.include_router(chat_router, prefix="/api/v1", tags=["chat"])


@app.get("/")
async def root():
    return {"message": "Chatbot API is online"}

