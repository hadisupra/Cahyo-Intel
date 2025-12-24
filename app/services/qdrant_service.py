"""Qdrant vector database service"""
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
        self.fallback_data = []  # Fallback in-memory storage
    
    def initialize(self):
        """Initialize Qdrant client and encoder"""
        try:
            # Try to import and initialize Qdrant
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams
            from sentence_transformers import SentenceTransformer
            
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
            logger.warning(f"Could not initialize Qdrant: {e}. Running in fallback mode with simple keyword search.")
            self.is_initialized = False
    
    def _create_collection_if_not_exists(self):
        """Create Qdrant collection if it doesn't exist"""
        try:
            from qdrant_client.models import Distance, VectorParams
            
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
        """Add documents to Qdrant collection or fallback storage"""
        if not self.is_initialized:
            # Store in fallback in-memory storage
            self.fallback_data = documents
            logger.info(f"Stored {len(documents)} documents in fallback storage")
            return
        
        try:
            from qdrant_client.models import PointStruct
            import uuid
            
            points = []
            for doc in documents:
                # Create text for embedding
                text = f"{doc.get('product_name', '')} {doc.get('product_description', '')} {doc.get('product_category', '')}"
                
                # Generate embedding
                embedding = self.encoder.encode(text).tolist()
                
                # Use product_id or generate UUID for unique point ID
                point_id = hash(doc.get('product_id', str(uuid.uuid4())))
                
                # Create point
                point = PointStruct(
                    id=point_id,
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
            # Use simple keyword search in fallback mode
            return self._fallback_search(query, top_k)
        
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
            return self._fallback_search(query, top_k)
    
    def _fallback_search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Simple keyword-based search for fallback mode"""
        if not self.fallback_data:
            return []
        
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        # Score each document based on keyword matches
        scored_docs = []
        for doc in self.fallback_data:
            text = f"{doc.get('product_name', '')} {doc.get('product_description', '')} {doc.get('product_category', '')}".lower()
            
            # Count matching words
            matches = sum(1 for word in query_words if word in text)
            
            if matches > 0:
                doc_copy = doc.copy()
                # Normalize score to 0-1 range
                doc_copy['similarity_score'] = min(matches / len(query_words), 1.0)
                scored_docs.append(doc_copy)
        
        # Sort by score and return top_k
        scored_docs.sort(key=lambda x: x['similarity_score'], reverse=True)
        return scored_docs[:top_k]
    
    def get_collection_info(self) -> Optional[Dict]:
        """Get information about the collection"""
        if not self.is_initialized:
            return {
                "mode": "fallback",
                "documents_count": len(self.fallback_data)
            }
        
        try:
            collection_info = self.client.get_collection(self.collection_name)
            # Safely extract vector count
            try:
                vectors_count = collection_info.vectors_count
            except AttributeError:
                vectors_count = 0
            
            return {
                "mode": "qdrant",
                "name": self.collection_name,
                "vectors_count": vectors_count,
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return None


# Global instance
qdrant_service = QdrantService()
