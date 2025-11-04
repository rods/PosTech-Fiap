from fastapi import FastAPI
from fastapi.responses import Response
from .routers import books, insights, users, ml, auth
from .internal.training_data import train_recommendation_model
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PosTech FIAP Book Recommendation API")

@app.on_event("startup")
async def startup_event():
    """Executa ao iniciar a aplicação"""
    logger.info("Iniciando aplicação...")
    
    try:
        train_recommendation_model()
        logger.info("Modelo treinado com sucesso no startup")
    except Exception as e:
        logger.error(f"Erro ao treinar modelo no startup: {e}")
        logger.warning("Aplicação continuará sem modelo treinado")

app.include_router(books.router)
app.include_router(insights.router)
app.include_router(users.router)
app.include_router(ml.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {
        "message": "PosTech FIAP Book Recommendation API",
        "description": "A comprehensive book recommendation system with machine learning capabilities",
        "version": "1.0.0",
        "available_apis": {
            "authentication": {
                "description": "User authentication and JWT token management",
                "endpoints": [
                    {
                        "method": "POST",
                        "path": "/api/v1/auth/login",
                        "description": "Login and get JWT token",
                        "requires_auth": False
                    },
                    {
                        "method": "GET", 
                        "path": "/api/v1/auth/status",
                        "description": "Check authentication service status",
                        "requires_auth": False
                    }
                ]
            },
            "books": {
                "description": "Book management and search functionality",
                "endpoints": [
                    {
                        "method": "GET",
                        "path": "/api/v1/books",
                        "description": "Get all book titles",
                        "requires_auth": False
                    },
                    {
                        "method": "GET",
                        "path": "/api/v1/books/{id}",
                        "description": "Get book by ID",
                        "requires_auth": False
                    },
                    {
                        "method": "POST",
                        "path": "/api/v1/books",
                        "description": "Create a new book",
                        "requires_auth": True
                    },
                    {
                        "method": "GET",
                        "path": "/api/v1/books/search",
                        "description": "Search books by title or category",
                        "parameters": "?title=string&category=string",
                        "requires_auth": False
                    },
                    {
                        "method": "GET",
                        "path": "/api/v1/books/top-rated",
                        "description": "Get books with rating >= 4",
                        "requires_auth": False
                    },
                    {
                        "method": "GET",
                        "path": "/api/v1/books/price-range",
                        "description": "Get books within price range",
                        "parameters": "?min=number&max=number",
                        "requires_auth": False
                    }
                ]
            },
            "categories": {
                "description": "Book category management",
                "endpoints": [
                    {
                        "method": "GET",
                        "path": "/api/v1/categories",
                        "description": "Get all available book categories",
                        "requires_auth": False
                    }
                ]
            },
            "users": {
                "description": "User management functionality",
                "endpoints": [
                    {
                        "method": "POST",
                        "path": "/api/v1/users/create",
                        "description": "Create a new user",
                        "parameters": "username, email, password",
                        "requires_auth": False
                    },
                    {
                        "method": "GET",
                        "path": "/api/v1/users/list/{username}",
                        "description": "Get user information by username",
                        "requires_auth": False
                    }
                ]
            },
            "machine_learning": {
                "description": "AI-powered book recommendations and ML features",
                "endpoints": [
                    {
                        "method": "GET",
                        "path": "/api/v1/ml/features",
                        "description": "Get ML feature data for all books",
                        "requires_auth": False
                    },
                    {
                        "method": "POST",
                        "path": "/api/v1/ml/predictions",
                        "description": "Get book recommendations based on a book title",
                        "parameters": "book_title (string)",
                        "requires_auth": False
                    }
                ]
            },
            "statistics": {
                "description": "Book collection statistics and insights",
                "endpoints": [
                    {
                        "method": "GET",
                        "path": "/api/v1/stats/overview",
                        "description": "Get general statistics (total books, prices, averages)",
                        "requires_auth": False
                    },
                    {
                        "method": "GET",
                        "path": "/api/v1/stats/categories",
                        "description": "Get statistics by category",
                        "requires_auth": False
                    }
                ]
            },
            "health": {
                "description": "API health monitoring",
                "endpoints": [
                    {
                        "method": "GET",
                        "path": "/api/v1/health",
                        "description": "Check API health status",
                        "requires_auth": False
                    }
                ]
            }
        },
        "getting_started": {
            "authentication": "Use POST /api/v1/auth/login with username='admin' and password='admin123' to get JWT token",
            "search_books": "Use GET /api/v1/books/search?title=BookName or ?category=CategoryName",
            "recommendations": "Use POST /api/v1/ml/predictions with book_title to get AI recommendations",
            "statistics": "Use GET /api/v1/stats/overview for general insights"
        }
    }

@app.get("/favicon.ico")
async def favicon():
    """Retorna resposta vazia para requisições de favicon"""
    return Response(status_code=204)

