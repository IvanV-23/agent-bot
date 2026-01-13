import logging

from sentence_transformers import SentenceTransformer, util
import torch

from app.services.tools import TOOLS
from app.services.guardrails import get_chat_response

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


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
    