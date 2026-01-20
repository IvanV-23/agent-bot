# app/services/guardrails.py
from nemoguardrails import LLMRails, RailsConfig

from app.core import globals

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
    globals.history.append({"role": "user", "content": message})

    response = await rails.generate_async(messages=list(globals.history))

    globals.history.append(response)
    
    return response


async def product_expert_response(product_data: dict):
    if rails is None:
        load_rails()
    
    # 2. Define the Sales Persona Prompt
    prompt = f"""
        You are a Sales Expert. Use the following data:
        Product: {product_data['name']}
        Price: {product_data['price']}
        Specs: {product_data['description']}
        
        Promote this product and explain its value.
    """
    globals.history.append({"role": "user", "content": prompt})

    response = await rails.generate_async(messages=list(globals.history))

    globals.history.append(response)
    
    return response
