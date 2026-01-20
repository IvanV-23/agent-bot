import os 
from qdrant_client import QdrantClient
from opentelemetry import trace
from sentence_transformers import SentenceTransformer


tracer = trace.get_tracer(__name__)

client = QdrantClient(path=os.getenv("QDRANT_PATH", r"D:/repos/chatbot/db/qdrant_storage"))

model = SentenceTransformer('all-MiniLM-L6-v2')

async def search_products(query: str):
    with tracer.start_as_current_span("qdrant_product_retrieval") as span:
        # Generate search vector
        query_vector = model.encode(query).tolist()
        
        # USE query_points INSTEAD OF search
        search_result = client.query_points(
            collection_name="products",
            query=query_vector, 
            limit=1
        )
        
        # Note: query_points returns a 'QueryResponse' object. 
        # We check the '.points' attribute.
        if search_result.points:
            product = search_result.points[0].payload
            span.set_attribute("search.found_product", product.get("name"))
            span.set_attribute("search.score", float(search_result.points[0].score))
            return product
        
        span.set_attribute("search.status", "not_found")
        return None
