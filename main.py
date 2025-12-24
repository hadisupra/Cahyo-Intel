"""
CAHYO Intelligence - Olist E-Commerce RAG System
Team Members: Hadi, Cristine, and Haryo
Final Project JCAI 001
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api import health, products, rag
from app.database.init_db import init_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    await init_database()
    yield
    # Shutdown (if needed)


app = FastAPI(
    title="CAHYO Intelligence - Olist E-Commerce RAG System",
    description="FastAPI with RAG Qdrant and SQLite Olist E-Commerce - Final Project JCAI 001",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware - Note: For production, restrict to specific domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: In production, replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(rag.router, prefix="/api/rag", tags=["RAG"])


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
