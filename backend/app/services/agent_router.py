import logging

from opentelemetry import trace
from sentence_transformers import SentenceTransformer, util
import torch

from app.services.tools import TOOLS
from app.services.guardrails import get_chat_response

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
tracer = trace.get_tracer(__name__)

classifier_model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')

ROUTES = {
    "weather": ["what is the weather like", "is it raining outside", "temperature today"],
    "time": ["calculate this", "what is the square root", "sum of these numbers"],
    "greeting": ["hello", "hi there", "good morning", "hey"]
}

ROUTE_EMBEDDINGS = {
    name: classifier_model.encode(examples, convert_to_tensor=True)
    for name, examples in ROUTES.items()
}

async def classify_query(user_input: str, threshold: float = 0.45) -> str:
    """
        Classify input and route to the appropriate answer.
    """
    with tracer.start_as_current_span("classify_query") as span:
        query_embedding = classifier_model.encode(user_input, convert_to_tensor=True)
            
        best_route = None
        highest_score = 0

        for route_name, embeddings in ROUTE_EMBEDDINGS.items():
            # Calculate cosine similarity
            cos_scores = util.cos_sim(query_embedding, embeddings)[0]
            max_score = torch.max(cos_scores).item()
            
            if max_score > highest_score:
                highest_score = max_score
                best_route = route_name

        intent = best_route if highest_score > threshold else "default_llm"
        span.set_attribute("input.value", user_input)
        span.set_attribute("classification.score", highest_score)
        span.set_attribute("classification.intent", intent)

        span.add_event("classification_completed", attributes={
                    "intent": intent,
                    "score": highest_score
                })

        if highest_score > threshold:
            return best_route
        return "default_llm"

async def handle_chat_routing(user_input: str):
    
    intent = await classify_query(user_input)

    logger.info(f"Classified intent: {intent} for input: {user_input}")

    if intent in TOOLS:
       
        tool = TOOLS[intent]
               
        if intent == "weather":
            
            city = user_input.split("in")[-1].strip() or "London"
            result = tool.invoke({"city": city})
            return {"type": "tool_result", "content": result, "tool": intent}
            
    result = await get_chat_response(user_input)

    return {"type": "llm_response", "content": result, "tool": "none"}
    