"""Database models for Olist E-Commerce"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Product(Base):
    """Product model for Olist E-Commerce"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String, unique=True, index=True)
    product_category = Column(String, index=True)
    product_name = Column(String)
    product_description = Column(Text)
    price = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Order(Base):
    """Order model for Olist E-Commerce"""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, unique=True, index=True)
    customer_id = Column(String, index=True)
    order_status = Column(String)
    order_date = Column(DateTime)
    total_amount = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class Customer(Base):
    """Customer model for Olist E-Commerce"""
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, unique=True, index=True)
    customer_city = Column(String)
    customer_state = Column(String)
    customer_zip_code = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
