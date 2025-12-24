# CAHYO Intelligence - Olist E-Commerce RAG System

**Final Project JCAI 001**

## Team Members
- **Hadi**
- **Cristine**
- **Haryo**

## Project Description

This is a comprehensive e-commerce recommendation system built with modern AI technologies. The project combines FastAPI for the backend API, Qdrant for vector database operations, and implements a RAG (Retrieval-Augmented Generation) system for intelligent product recommendations based on the Olist E-Commerce dataset.

## Features

- **FastAPI Backend**: Modern, fast (high-performance) web framework for building APIs
- **RAG System**: Retrieval-Augmented Generation for intelligent query processing
- **Qdrant Vector Database**: Efficient similarity search for product recommendations
- **SQLite Database**: Persistent storage for products, orders, and customer data
- **Semantic Search**: Find products using natural language queries
- **RESTful API**: Well-documented endpoints for all operations

## Technology Stack

- **Backend Framework**: FastAPI
- **Vector Database**: Qdrant
- **Relational Database**: SQLite with SQLAlchemy ORM
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **API Documentation**: Swagger UI / ReDoc
- **Python**: 3.8+

## Project Structure

```
Cahyo-Intel/
├── app/
│   ├── api/              # API endpoints
│   │   ├── health.py     # Health check endpoint
│   │   ├── products.py   # Product-related endpoints
│   │   └── rag.py        # RAG system endpoints
│   ├── database/         # Database layer
│   │   ├── database.py   # Database connection
│   │   ├── models.py     # SQLAlchemy models
│   │   └── init_db.py    # Database initialization
│   ├── models/           # Pydantic models
│   │   └── schemas.py    # API schemas
│   ├── services/         # Business logic
│   │   ├── qdrant_service.py  # Qdrant operations
│   │   └── rag_service.py     # RAG implementation
│   └── config.py         # Configuration management
├── data/                 # Data directory
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variables template
└── README.md           # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- (Optional) Qdrant running locally or via Docker

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/hadisupra/Cahyo-Intel.git
   cd Cahyo-Intel
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run Qdrant (Optional but recommended for full RAG functionality)**
   
   Using Docker:
   ```bash
   docker run -p 6333:6333 qdrant/qdrant
   ```
   
   Or download from: https://qdrant.tech/documentation/quick-start/

## Running the Application

### Option 1: Running Locally

1. **Start the FastAPI server**
   ```bash
   python main.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Access the application**
   - API Documentation (Swagger UI): http://localhost:8000/docs
   - Alternative API Docs (ReDoc): http://localhost:8000/redoc
   - Root endpoint: http://localhost:8000/

### Option 2: Running with Docker Compose (Recommended)

This method automatically sets up both the application and Qdrant vector database.

1. **Build and start services**
   ```bash
   docker-compose up -d
   ```

2. **Access the application**
   - API Documentation: http://localhost:8000/docs
   - Qdrant Dashboard: http://localhost:6333/dashboard

3. **Stop services**
   ```bash
   docker-compose down
   ```

### Option 3: Running Only Qdrant with Docker

If you want to run Qdrant separately:

```bash
docker run -p 6333:6333 qdrant/qdrant
```

Then start the FastAPI application locally as shown in Option 1.

## API Endpoints

### Health & Info
- `GET /` - Root endpoint with team information
- `GET /health` - Health check endpoint

### Products
- `GET /api/products/` - Get all products (with pagination and filtering)
- `GET /api/products/{product_id}` - Get specific product
- `GET /api/products/categories/list` - Get all product categories
- `GET /api/products/orders/all` - Get all orders
- `GET /api/products/customers/all` - Get all customers

### RAG System
- `POST /api/rag/query` - Query the RAG system for product recommendations
  ```json
  {
    "query": "I need a laptop for programming",
    "top_k": 5
  }
  ```
- `POST /api/rag/index` - Index products into vector database
- `GET /api/rag/status` - Get RAG system status

## Usage Examples

### Query Products with Natural Language

```bash
curl -X POST "http://localhost:8000/api/rag/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "I want to buy a smartphone with good camera",
    "top_k": 3
  }'
```

### Get All Products

```bash
curl "http://localhost:8000/api/products/"
```

### Get Products by Category

```bash
curl "http://localhost:8000/api/products/?category=Electronics"
```

### Running the Test Suite

The project includes a comprehensive test suite:

```bash
python test_api.py
```

This will test all endpoints and display formatted responses.

## Database Schema

### Products Table
- `id`: Primary key
- `product_id`: Unique product identifier
- `product_category`: Product category
- `product_name`: Product name
- `product_description`: Detailed description
- `price`: Product price
- `created_at`, `updated_at`: Timestamps

### Orders Table
- `id`: Primary key
- `order_id`: Unique order identifier
- `customer_id`: Reference to customer
- `order_status`: Order status
- `order_date`: Order date
- `total_amount`: Total order amount

### Customers Table
- `id`: Primary key
- `customer_id`: Unique customer identifier
- `customer_city`, `customer_state`: Location
- `customer_zip_code`: Postal code

## RAG System

The RAG (Retrieval-Augmented Generation) system works as follows:

1. **Indexing**: Products are converted to embeddings using Sentence Transformers
2. **Storage**: Embeddings are stored in Qdrant vector database
3. **Retrieval**: User queries are converted to embeddings and similar products are found
4. **Generation**: Retrieved products are formatted into natural language responses

### Fallback Mode

The system includes a **fallback mode** that works even when Qdrant is not available:
- Uses simple keyword-based search instead of semantic search
- Stores product data in memory
- Provides basic but functional product recommendations
- No external dependencies required

This makes the system robust and usable in any environment!

## Development Notes

- The application automatically initializes the database with sample data on first run
- Qdrant is optional - the system will run in fallback mode if Qdrant is not available
- For production, add proper authentication and rate limiting
- Consider adding Redis for caching in production environments

## Contributing

This is a final project for JCAI 001. For questions or collaboration, please contact the team members.

## License

This project is created for educational purposes as part of JCAI 001 Final Project.

## Acknowledgments

- JCAI 001 Course
- Olist E-Commerce Dataset
- FastAPI Framework
- Qdrant Vector Database
- Sentence Transformers

---

**Built with ❤️ by Team CAHYO Intelligence**
