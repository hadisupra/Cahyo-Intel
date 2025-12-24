"""
CAHYO Intelligence - Olist E-Commerce RAG System
Team Members: Hadi, Cristine, and Haryo
Final Project JCAI 001
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import health, products, rag
from app.database.init_db import init_database

app = FastAPI(
    title="CAHYO Intelligence - Olist E-Commerce RAG System",
    description="FastAPI with RAG Qdrant and SQLite Olist E-Commerce - Final Project JCAI 001",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(rag.router, prefix="/api/rag", tags=["RAG"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_database()


@app.get("/")
async def root():
    """Root endpoint with team information"""
    return {
        "message": "Welcome to CAHYO Intelligence - Olist E-Commerce RAG System",
        "team": "CAHYO Intelligence",
        "members": ["Hadi", "Cristine", "Haryo"],
        "project": "Final Project JCAI 001",
        "description": "FastAPI with RAG Qdrant and SQLite Olist E-Commerce",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
