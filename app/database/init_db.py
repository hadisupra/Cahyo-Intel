"""Database initialization with sample data"""
from app.database.database import create_tables, AsyncSessionLocal
from app.database.models import Product, Order, Customer
from datetime import datetime, timedelta
import random


async def init_database():
    """Initialize database and populate with sample data"""
    # Create tables
    await create_tables()
    
    # Check if data already exists
    async with AsyncSessionLocal() as session:
        result = await session.execute("SELECT COUNT(*) FROM products")
        count = result.scalar()
        
        if count > 0:
            print("Database already initialized")
            return
    
    # Add sample data
    await add_sample_products()
    await add_sample_customers()
    await add_sample_orders()
    print("Database initialized with sample data")


async def add_sample_products():
    """Add sample products to database"""
    sample_products = [
        {
            "product_id": "PROD001",
            "product_category": "Electronics",
            "product_name": "Smartphone X1",
            "product_description": "High-performance smartphone with 6.5 inch display, 128GB storage, and advanced camera system",
            "price": 599.99
        },
        {
            "product_id": "PROD002",
            "product_category": "Electronics",
            "product_name": "Laptop Pro",
            "product_description": "Professional laptop with Intel i7 processor, 16GB RAM, 512GB SSD, perfect for work and gaming",
            "price": 1299.99
        },
        {
            "product_id": "PROD003",
            "product_category": "Home & Garden",
            "product_name": "Coffee Maker Deluxe",
            "product_description": "Premium coffee maker with programmable timer, 12-cup capacity, and auto shut-off feature",
            "price": 89.99
        },
        {
            "product_id": "PROD004",
            "product_category": "Fashion",
            "product_name": "Designer Jeans",
            "product_description": "Comfortable and stylish designer jeans made from premium denim fabric",
            "price": 79.99
        },
        {
            "product_id": "PROD005",
            "product_category": "Books",
            "product_name": "Python Programming Guide",
            "product_description": "Comprehensive guide to Python programming for beginners and advanced users",
            "price": 39.99
        },
        {
            "product_id": "PROD006",
            "product_category": "Electronics",
            "product_name": "Wireless Headphones",
            "product_description": "Premium wireless headphones with noise cancellation and 30-hour battery life",
            "price": 249.99
        },
        {
            "product_id": "PROD007",
            "product_category": "Sports",
            "product_name": "Yoga Mat Premium",
            "product_description": "Eco-friendly yoga mat with superior grip and cushioning for comfortable practice",
            "price": 45.99
        },
        {
            "product_id": "PROD008",
            "product_category": "Home & Garden",
            "product_name": "LED Smart Bulb",
            "product_description": "Smart LED bulb with WiFi connectivity, voice control, and customizable colors",
            "price": 24.99
        },
    ]
    
    async with AsyncSessionLocal() as session:
        for product_data in sample_products:
            product = Product(**product_data)
            session.add(product)
        await session.commit()


async def add_sample_customers():
    """Add sample customers to database"""
    sample_customers = [
        {
            "customer_id": "CUST001",
            "customer_city": "Sao Paulo",
            "customer_state": "SP",
            "customer_zip_code": "01310-100"
        },
        {
            "customer_id": "CUST002",
            "customer_city": "Rio de Janeiro",
            "customer_state": "RJ",
            "customer_zip_code": "20040-020"
        },
        {
            "customer_id": "CUST003",
            "customer_city": "Brasilia",
            "customer_state": "DF",
            "customer_zip_code": "70040-020"
        },
        {
            "customer_id": "CUST004",
            "customer_city": "Belo Horizonte",
            "customer_state": "MG",
            "customer_zip_code": "30130-100"
        },
        {
            "customer_id": "CUST005",
            "customer_city": "Curitiba",
            "customer_state": "PR",
            "customer_zip_code": "80020-100"
        },
    ]
    
    async with AsyncSessionLocal() as session:
        for customer_data in sample_customers:
            customer = Customer(**customer_data)
            session.add(customer)
        await session.commit()


async def add_sample_orders():
    """Add sample orders to database"""
    statuses = ["delivered", "shipped", "processing", "pending"]
    
    sample_orders = []
    for i in range(1, 11):
        order = {
            "order_id": f"ORD{i:04d}",
            "customer_id": f"CUST{random.randint(1, 5):03d}",
            "order_status": random.choice(statuses),
            "order_date": datetime.utcnow() - timedelta(days=random.randint(1, 60)),
            "total_amount": round(random.uniform(50, 1500), 2)
        }
        sample_orders.append(order)
    
    async with AsyncSessionLocal() as session:
        for order_data in sample_orders:
            order = Order(**order_data)
            session.add(order)
        await session.commit()
