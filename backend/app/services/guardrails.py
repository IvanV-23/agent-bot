# app/services/guardrails.py
from nemoguardrails import LLMRails, RailsConfig


# Global variable to hold the rails instance
rails = None

def load_rails():
    global rails
    config = RailsConfig.from_path("./rails")
    rails = LLMRails(config)
    return rails

async def get_chat_response(message: str):
    if rails is None:
        load_rails()
    
    # NeMo Guardrails uses its internal logic (Colang) to decide
    # if it should call the LLM or return a canned response.
    response = await rails.generate_async(messages=[{
        "role": "user", 
        "content": message
    }])
    
    return response
