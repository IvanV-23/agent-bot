from collections import deque

from fastapi import FastAPI
from app.api.chat import router as chat_router
from phoenix.otel import register
from openinference.instrumentation.langchain import LangChainInstrumentor

from app.core import globals

globals.history = deque(maxlen=5)  # Store last 10 interactions

app = FastAPI(
    title="Ivabot",
    version="1.0.0"
)

tracer_provider = register(auto_instrument=True)
LangChainInstrumentor().instrument(tracer_provider=tracer_provider)

# 2. Include API routes
app.include_router(chat_router, prefix="/api/v1", tags=["chat"])


@app.get("/")
async def root():
    return {"message": "Chatbot API is online"}

