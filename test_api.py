"""
API Test Examples for CAHYO Intelligence - Olist E-Commerce RAG System
This file contains example API calls for testing the system
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def print_response(title, response):
    """Helper function to print formatted responses"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except json.JSONDecodeError:
        print(response.text)
    print(f"{'='*60}\n")


def test_root():
    """Test root endpoint"""
    response = requests.get(f"{BASE_URL}/")
    print_response("ROOT ENDPOINT", response)


def test_health():
    """Test health check endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print_response("HEALTH CHECK", response)


def test_get_products():
    """Test get all products"""
    response = requests.get(f"{BASE_URL}/api/products/")
    print_response("GET ALL PRODUCTS", response)


def test_get_product_by_id():
    """Test get specific product"""
    response = requests.get(f"{BASE_URL}/api/products/PROD001")
    print_response("GET PRODUCT BY ID (PROD001)", response)


def test_get_categories():
    """Test get categories"""
    response = requests.get(f"{BASE_URL}/api/products/categories/list")
    print_response("GET CATEGORIES", response)


def test_get_products_by_category():
    """Test get products by category"""
    response = requests.get(f"{BASE_URL}/api/products/?category=Electronics")
    print_response("GET PRODUCTS BY CATEGORY (Electronics)", response)


def test_get_orders():
    """Test get all orders"""
    response = requests.get(f"{BASE_URL}/api/products/orders/all")
    print_response("GET ALL ORDERS", response)


def test_get_customers():
    """Test get all customers"""
    response = requests.get(f"{BASE_URL}/api/products/customers/all")
    print_response("GET ALL CUSTOMERS", response)


def test_rag_status():
    """Test RAG system status"""
    response = requests.get(f"{BASE_URL}/api/rag/status")
    print_response("RAG SYSTEM STATUS", response)


def test_index_products():
    """Test index products into RAG system"""
    response = requests.post(f"{BASE_URL}/api/rag/index")
    print_response("INDEX PRODUCTS", response)


def test_rag_query():
    """Test RAG query"""
    query_data = {
        "query": "I need a laptop for programming",
        "top_k": 3
    }
    response = requests.post(
        f"{BASE_URL}/api/rag/query",
        json=query_data,
        headers={"Content-Type": "application/json"}
    )
    print_response("RAG QUERY - Laptop for programming", response)


def test_rag_query_smartphone():
    """Test RAG query for smartphone"""
    query_data = {
        "query": "smartphone with good camera",
        "top_k": 2
    }
    response = requests.post(
        f"{BASE_URL}/api/rag/query",
        json=query_data,
        headers={"Content-Type": "application/json"}
    )
    print_response("RAG QUERY - Smartphone with camera", response)


def test_rag_query_home():
    """Test RAG query for home products"""
    query_data = {
        "query": "coffee maker",
        "top_k": 2
    }
    response = requests.post(
        f"{BASE_URL}/api/rag/query",
        json=query_data,
        headers={"Content-Type": "application/json"}
    )
    print_response("RAG QUERY - Coffee maker", response)


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("CAHYO Intelligence - API Test Suite")
    print("Team: Hadi, Cristine, Haryo")
    print("Final Project JCAI 001")
    print("="*60 + "\n")
    
    try:
        # Basic endpoints
        test_root()
        test_health()
        
        # Product endpoints
        test_get_products()
        test_get_product_by_id()
        test_get_categories()
        test_get_products_by_category()
        
        # Order and customer endpoints
        test_get_orders()
        test_get_customers()
        
        # RAG endpoints
        test_rag_status()
        test_index_products()
        test_rag_query()
        test_rag_query_smartphone()
        test_rag_query_home()
        
        print("\n" + "="*60)
        print("ALL TESTS COMPLETED")
        print("="*60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to the API server.")
        print("Please make sure the server is running on http://localhost:8000")
        print("Start the server with: python main.py")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")


if __name__ == "__main__":
    run_all_tests()
