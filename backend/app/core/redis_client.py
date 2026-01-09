# app/core/redis_client.py
from langchain_redis import RedisSemanticCache
from langchain_openai import OpenAIEmbeddings # Or your local embeddings
from langchain.globals import set_llm_cache

def init_redis_cache():
    # This sets the GLOBAL cache for all LangChain LLM calls
    cache = RedisSemanticCache(
        redis_url="redis://localhost:6379",
        embeddings=OpenAIEmbeddings(), # This converts questions into vectors
        distance_threshold=0.1         # Lower = more strict similarity
    )
    set_llm_cache(cache)
    print("Redis Semantic Cache initialized.")
