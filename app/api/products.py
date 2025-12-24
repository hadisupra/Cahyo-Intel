"""Products API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database.database import get_db
from app.database.models import Product, Order, Customer
from app.models.schemas import ProductResponse, OrderResponse, CustomerResponse

router = APIRouter()


@router.get("/", response_model=List[ProductResponse])
async def get_products(
    skip: int = 0,
    limit: int = 100,
    category: str = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all products with optional filtering"""
    query = select(Product)
    
    if category:
        query = query.where(Product.product_category == category)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    products = result.scalars().all()
    
    return products


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific product by ID"""
    query = select(Product).where(Product.product_id == product_id)
    result = await db.execute(query)
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product


@router.get("/categories/list")
async def get_categories(db: AsyncSession = Depends(get_db)):
    """Get all product categories"""
    query = select(Product.product_category).distinct()
    result = await db.execute(query)
    categories = result.scalars().all()
    
    return {"categories": categories}


@router.get("/orders/all", response_model=List[OrderResponse])
async def get_orders(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all orders"""
    query = select(Order).offset(skip).limit(limit)
    result = await db.execute(query)
    orders = result.scalars().all()
    
    return orders


@router.get("/customers/all", response_model=List[CustomerResponse])
async def get_customers(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all customers"""
    query = select(Customer).offset(skip).limit(limit)
    result = await db.execute(query)
    customers = result.scalars().all()
    
    return customers
