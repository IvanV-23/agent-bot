import logging
import re
import inspect

from opentelemetry import trace
from sentence_transformers import SentenceTransformer


from app.services.search_products import search_products
from app.services.guardrails import generate_dynamic_tool, product_expert_response

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
tracer = trace.get_tracer(__name__)

classifier_model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')


PURCHASE_TOOLS = ["calculate", "roi", "discount", "total", "shipping", "bulk"]




async def purchase_router(user_input: str, product_data: str) -> bool:
    """
        Determine if the input is related to purchase tools.
    """
    with tracer.start_as_current_span("purchase_router") as span:
        is_calculation_requested = any(keyword in user_input.lower() for keyword in PURCHASE_TOOLS)

        if is_calculation_requested:
            span.set_attribute("purchase_router.matched_keyword", "calculation_request")
            span.set_attribute("purchase_router.user_input", user_input) 
            logger.info("Routing to DYNAMIC TOOL GENERATOR")
            # Step A: Generate the tool JSON
            dynamic_tool_json = await generate_dynamic_tool(user_input)

            #dynamic_tool_json = get_tool_json(dynamic_tool_json)
            
            if dynamic_tool_json:
                # Step B: Execute the code safely
                # Note: In a real app, use a safer eval method
                logger.info(f"Generated dynamic tool: {dynamic_tool_json}")
                try:
                    nums = re.findall(r'\d+', user_input)
                    quantity = int(nums[0]) if nums else 10 # Default to 10 if they just say "bulk"

                    calc_func = eval(dynamic_tool_json['python_code'])
                        
                    # Get the number of arguments the lambda actually wants
                    sig = inspect.signature(calc_func)
                    num_params = len(sig.parameters)

                    if num_params == 2:
                        # If the LLM included a discount/tax parameter
                        total_cost = calc_func(quantity, 0.15) 
                    else:
                        # If the LLM hardcoded the tax (like in your log)
                        total_cost = calc_func(quantity)


                    product_data['calculation_result'] = f"Total cost for {quantity} units is ${total_cost:.2f}"

                    response = await product_expert_response(product_data)
                    if hasattr(response, 'content'):
                        return response.content
                    elif isinstance(response, dict) and 'content' in response:
                        return response['content']
                    else:
                        # If it's already a string, just return it
                        return str(response)              
                except Exception as e:
                    logger.error(f"Execution error: {e}")
                    return "There was an error calculating the requested information."
        
        
        response = await product_expert_response(product_data)

        span.set_attribute("purchase_router.matched_keyword", "none")
        span.set_attribute("purchase_router.user_input", user_input)

        return response
    
        # 2. Fallback to Product Search (Qdrant) if info/lookup is requested
        #logger.info("Routing to QDRANT SEARCH")
    
        #product_data = await search_products(user_input)
        
        #if product_data:
            # Step C: Use the Sales Expert Persona to format the RAG result
        #    sales_response = await product_expert_response(product_data)
        #    return {"type": "sales_pitch", "content": sales_response}


        #span.set_attribute("purchase_router.matched_keyword", "none")
        #return {"type": "fallback", "content": "I couldn't find that specific product. Can you tell me more?"}
