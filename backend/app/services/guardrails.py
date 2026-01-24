# app/services/guardrails.py
import json
import logging
import re
from urllib import response

from nemoguardrails import LLMRails, RailsConfig
from jsonschema import validate, ValidationError

from app.core import globals

# Global variable to hold the rails instance
rails = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOOL_SCHEMA = {
    "type": "object",
    "properties": {
        "tool_name": {"type": "string"},
        "parameters": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "type": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["name", "type"]
            }
        },
        "python_code": {"type": "string"}
    },
    "required": ["tool_name", "parameters", "python_code"]
}


async def check_code_safety(code: str):
    forbidden = ["os.", "sys.", "subprocess", "open(", "pathlib", "socket", "rmdir"]
    for term in forbidden:
        if term in code.lower():
            return False  # Danger detected
    return True # Safe to proceed


def load_rails():
    global rails
    config = RailsConfig.from_path("./rails")
    rails = LLMRails(config)

    # 2. REGISTER THE ACTION
    # This maps the Colang "execute check_code_safety" to this Python function
    rails.register_action(check_code_safety, name="check_code_safety")

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
    
    # Define a more descriptive prompt for the 'Sales Expert' persona
    prompt = f"""SYSTEM: You are a senior Industrial Sales Engineer.
        DATA:
        - Product: {product_data['name']}
        - Base Price: {product_data['price']}
        - Specs: {product_data['description']}
        - Calculation: {product_data.get('calculation_result', 'N/A')}
        - Context: {product_data['sales_context']}
        
        USER: Convert this data into a professional sales response. 
        Follow these instructions:
        1. Acknowledge the quantity.
        2. Mention the stainless steel casing and vibration reduction benefits.
        3. State the total cost clearly.
        4. Provide a call to action.

        ASSISTANT:"""
    
    # Ensure history management is clean
    globals.history.append({"role": "user", "content": prompt})

    # Generate the response using your Rails instance
    response = await rails.generate_async(messages=list(globals.history))
    #response = await rails.llm.ainvoke(prompt)
    
    if isinstance(response, dict):
        bot_text = response.get("content", "")
    elif hasattr(response, "content"):
        bot_text = response.content
    else:
        bot_text = str(response)
    # response is usually an object, extract the text content
    bot_text = response.content if hasattr(response, 'content') else response
    
    globals.history.append({"role": "assistant", "content": bot_text})
    
    return bot_text

async def generate_dynamic_tool(user_request: str, retries: int = 10):
    if rails is None:
        load_rails()

    # 1. Define the Strict Prompt
    prompt = f"""SYSTEM:
                    You are a Technical Architect. Your only job is to output a Python tool definition in a strict JSON format. 
                    Do not include any introductory text, markdown formatting, or explanations.
                    Output ONLY the JSON object.

                    The JSON must follow this schema:
                    {{
                    "tool_name": "string",
                    "parameters": [{{ "name": "string", "type": "string", "description": "string" }}],
                    "python_code": "A single line string containing the lambda or function logic"
                    }}

                    USER:
                    Create a dynamic tool that calculates the total cost of multiple PX-500 pumps including a 15% industrial tax.

                    ASSISTANT:
                    {{
                    "tool_name": "calculate_pump_investment",
                    "parameters": [
                        {{ "name": "quantity", "type": "int", "description": "Number of pumps" }}
                    ],
                    "python_code": "lambda quantity: (quantity * 1200) * 0.9"
                    }}

                    USER:
                    {user_request}

                    ASSISTANT:{{"""

    # 2. Call the LLM directly through the rails instance
    # We use temperature 0 for maximum precision (no creativity allowed here)

    for attempt in range(retries):
        # 3. Clean and Parse
        last_error = ""
        try:
            if last_error != "":
                logger.info(f"Retrying dynamic tool generation, attempt {attempt + 1}")
                prompt += f"\n\n# Previous error: {last_error}\n# Please correct the JSON format.\nASSISTANT:{{"
            response = await rails.llm.ainvoke(prompt, stop=["USER:", "ASSISTANT:"])
            response_text = response.content
            # This regex is specifically designed to find the first '{' 
            # and match it with the last '}' in the string, ignoring anything after.
            match = re.search(r'(\{.*\})', response_text.strip(), re.DOTALL)
            
            if match:
                clean_json = match.group(1)
                # Final safety: remove potential trailing newlines/chatter
                tool_json = json.loads(clean_json)
                #validate(instance=tool_json, schema=TOOL_SCHEMA)
            
                return tool_json # Success!
            else:
                # If no braces found, the LLM failed the format entirely
                logging.error(f"Raw Response missing JSON braces: {response_text}")
                last_error = f"Raw Response missing JSON braces: {response_text}"
                attempt += 1
        except json.JSONDecodeError as e:
            # This is where 'Extra data' is caught. 
            # Usually happens if the LLM output something like: { "json": "data" } I hope this helps!
            logging.error(f"JSON Decode Error at pos {e.pos}: {e.msg}")
            attempt += 1
            last_error = f"JSON Decode Error at pos {e.pos}: {e.msg}"

    return None
