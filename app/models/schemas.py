"""Pydantic schemas for API requests and responses"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ProductBase(BaseModel):
    """Base product schema"""
    product_id: str
    product_category: str
    product_name: str
    product_description: Optional[str] = None
    price: float


class ProductCreate(ProductBase):
    """Product creation schema"""
    pass


class ProductResponse(ProductBase):
    """Product response schema"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    """Order response schema"""
    id: int
    order_id: str
    customer_id: str
    order_status: str
    order_date: datetime
    total_amount: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class CustomerResponse(BaseModel):
    """Customer response schema"""
    id: int
    customer_id: str
    customer_city: str
    customer_state: str
    customer_zip_code: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class RAGQuery(BaseModel):
    """RAG query request schema"""
    query: str = Field(..., description="User query for RAG system")
    top_k: int = Field(default=5, description="Number of relevant documents to retrieve")


class RAGResponse(BaseModel):
    """RAG response schema"""
    query: str
    answer: str
    relevant_products: List[dict]
    confidence: float = Field(default=0.0, description="Confidence score of the answer")
