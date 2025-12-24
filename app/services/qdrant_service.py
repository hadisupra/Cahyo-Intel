"""Qdrant vector database service"""
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class QdrantService:
    """Service for managing Qdrant vector database operations"""
    
    def __init__(self):
        self.client = None
        self.encoder = None
        self.collection_name = settings.qdrant_collection_name
        self.is_initialized = False
    
    def initialize(self):
        """Initialize Qdrant client and encoder"""
        try:
            # Initialize Qdrant client
            self.client = QdrantClient(
                host=settings.qdrant_host,
                port=settings.qdrant_port,
                timeout=10
            )
            
            # Initialize sentence transformer for embeddings
            self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Create collection if it doesn't exist
            self._create_collection_if_not_exists()
            
            self.is_initialized = True
            logger.info("Qdrant service initialized successfully")
        except Exception as e:
            logger.warning(f"Could not initialize Qdrant: {e}. Running in fallback mode.")
            self.is_initialized = False
    
    def _create_collection_if_not_exists(self):
        """Create Qdrant collection if it doesn't exist"""
        try:
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=384,  # all-MiniLM-L6-v2 produces 384-dimensional vectors
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            raise
    
    def add_documents(self, documents: List[Dict]):
        """Add documents to Qdrant collection"""
        if not self.is_initialized:
            logger.warning("Qdrant not initialized, skipping document addition")
            return
        
        try:
            points = []
            for idx, doc in enumerate(documents):
                # Create text for embedding
                text = f"{doc.get('product_name', '')} {doc.get('product_description', '')} {doc.get('product_category', '')}"
                
                # Generate embedding
                embedding = self.encoder.encode(text).tolist()
                
                # Create point
                point = PointStruct(
                    id=idx,
                    vector=embedding,
                    payload=doc
                )
                points.append(point)
            
            # Upload points to Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            logger.info(f"Added {len(points)} documents to Qdrant")
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for similar documents"""
        if not self.is_initialized:
            logger.warning("Qdrant not initialized, returning empty results")
            return []
        
        try:
            # Generate query embedding
            query_vector = self.encoder.encode(query).tolist()
            
            # Search in Qdrant
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k
            )
            
            # Extract relevant information
            documents = []
            for result in results:
                doc = result.payload
                doc['similarity_score'] = result.score
                documents.append(doc)
            
            return documents
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    def get_collection_info(self) -> Optional[Dict]:
        """Get information about the collection"""
        if not self.is_initialized:
            return None
        
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                "name": collection_info.config.params.vectors.size if collection_info.config.params.vectors else 0,
                "vectors_count": collection_info.vectors_count if hasattr(collection_info, 'vectors_count') else 0,
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return None


# Global instance
qdrant_service = QdrantService()
