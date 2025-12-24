"""Health check endpoint"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "CAHYO Intelligence - Olist E-Commerce RAG System",
        "team": ["Hadi", "Cristine", "Haryo"],
        "project": "Final Project JCAI 001"
    }
