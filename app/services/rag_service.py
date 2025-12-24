"""RAG (Retrieval-Augmented Generation) service"""
from typing import List, Dict
from app.services.qdrant_service import qdrant_service
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class RAGService:
    """Service for RAG operations"""
    
    def __init__(self):
        self.qdrant = qdrant_service
    
    def generate_answer(self, query: str, relevant_docs: List[Dict]) -> str:
        """Generate answer based on query and relevant documents"""
        if not relevant_docs:
            return "I couldn't find any relevant products for your query. Please try a different search term."
        
        # Build context from relevant documents
        context_parts = []
        for doc in relevant_docs:
            product_info = f"Product: {doc.get('product_name', 'Unknown')}\n"
            product_info += f"Category: {doc.get('product_category', 'Unknown')}\n"
            product_info += f"Price: ${doc.get('price', 0):.2f}\n"
            product_info += f"Description: {doc.get('product_description', 'No description available')}\n"
            context_parts.append(product_info)
        
        context = "\n---\n".join(context_parts)
        
        # For now, return a formatted response with the context
        # In a production system, this would call an LLM API
        answer = f"Based on your query '{query}', I found the following relevant products:\n\n{context}"
        
        return answer
    
    async def query(self, query: str, top_k: int = 5) -> Dict:
        """Process RAG query"""
        try:
            # Search for relevant documents
            relevant_docs = self.qdrant.search(query, top_k=top_k)
            
            # Generate answer
            answer = self.generate_answer(query, relevant_docs)
            
            # Calculate confidence based on similarity scores
            confidence = 0.0
            if relevant_docs:
                scores = [doc.get('similarity_score', 0) for doc in relevant_docs]
                confidence = sum(scores) / len(scores) if scores else 0.0
            
            return {
                "query": query,
                "answer": answer,
                "relevant_products": relevant_docs,
                "confidence": confidence
            }
        except Exception as e:
            logger.error(f"Error processing RAG query: {e}")
            return {
                "query": query,
                "answer": f"An error occurred while processing your query: {str(e)}",
                "relevant_products": [],
                "confidence": 0.0
            }
    
    async def index_products(self, products: List[Dict]):
        """Index products into vector database"""
        try:
            self.qdrant.add_documents(products)
            logger.info(f"Indexed {len(products)} products")
        except Exception as e:
            logger.error(f"Error indexing products: {e}")


# Global instance
rag_service = RAGService()
