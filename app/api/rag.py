"""RAG API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.database import get_db
from app.database.models import Product
from app.models.schemas import RAGQuery, RAGResponse
from app.services.rag_service import rag_service
from app.services.qdrant_service import qdrant_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/query", response_model=RAGResponse)
async def rag_query(query: RAGQuery, db: AsyncSession = Depends(get_db)):
    """
    Query the RAG system for product recommendations and information.
    
    This endpoint uses semantic search to find relevant products and 
    generates a natural language response based on the query.
    
    Note: If Qdrant is not available, the system will use a simple keyword-based
    search as a fallback.
    """
    try:
        # Process RAG query (will use fallback mode if not initialized)
        result = await rag_service.query(query.query, query.top_k)
        
        return RAGResponse(**result)
    except Exception as e:
        logger.error(f"Error in RAG query: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.post("/index")
async def index_products_endpoint(db: AsyncSession = Depends(get_db)):
    """
    Index all products into the vector database.
    
    This endpoint should be called when new products are added to ensure
    they are searchable via the RAG system.
    
    Note: This requires Qdrant to be running. If Qdrant is not available,
    products will be stored in fallback in-memory storage for keyword search.
    """
    try:
        # Initialize Qdrant if not already done (may fail if Qdrant not running)
        if not qdrant_service.is_initialized:
            qdrant_service.initialize()
        
        # Get all products from database
        query = select(Product)
        result = await db.execute(query)
        products = result.scalars().all()
        
        # Convert to dict format
        product_dicts = []
        for product in products:
            product_dicts.append({
                "id": product.id,
                "product_id": product.product_id,
                "product_name": product.product_name,
                "product_category": product.product_category,
                "product_description": product.product_description,
                "price": product.price
            })
        
        # Index products
        await rag_service.index_products(product_dicts)
        
        mode = "Qdrant" if qdrant_service.is_initialized else "fallback in-memory storage"
        
        return {
            "status": "success",
            "message": f"Indexed {len(product_dicts)} products in {mode}",
            "count": len(product_dicts),
            "mode": mode
        }
    except Exception as e:
        logger.error(f"Error indexing products: {e}")
        raise HTTPException(status_code=500, detail=f"Error indexing products: {str(e)}")


@router.get("/status")
async def rag_status():
    """Get RAG system status"""
    try:
        if not qdrant_service.is_initialized:
            return {
                "status": "fallback_mode",
                "qdrant_initialized": False,
                "mode": "keyword_search",
                "message": "RAG system is running in fallback mode with keyword search. Qdrant is not available."
            }
        
        collection_info = qdrant_service.get_collection_info()
        
        return {
            "status": "operational",
            "qdrant_initialized": True,
            "mode": "semantic_search",
            "collection_info": collection_info,
            "message": "RAG system is operational with semantic search"
        }
    except Exception as e:
        logger.error(f"Error getting RAG status: {e}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Error getting RAG system status"
        }
