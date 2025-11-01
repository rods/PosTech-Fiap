from fastapi import FastAPI
<<<<<<< HEAD
from fastapi.responses import Response
from .routers import books, insights, users, ml
from .internal.training_data import train_recommendation_model
import boto3 
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
=======
from .routers import books,insights
from app.routers.auth import router as auth_router
from app.models.database import Base, engine
>>>>>>> f634bdb28beaf0c91b110580539c4b8437841448

Base.metadata.create_all(bind=engine)

app = FastAPI(title="JWT Protected API")

@app.on_event("startup")
async def startup_event():
    """Executa ao iniciar a aplicação"""
    logger.info("Iniciando aplicação...")
    
    try:
        # Treina o modelo ao iniciar
        train_recommendation_model()
        logger.info("Modelo treinado com sucesso no startup")
    except Exception as e:
        logger.error(f"Erro ao treinar modelo no startup: {e}")
        logger.warning("Aplicação continuará sem modelo treinado")

app.include_router(books.router)
app.include_router(insights.router)
<<<<<<< HEAD
app.include_router(users.router)
app.include_router(ml.router)

@app.get("/favicon.ico")
async def favicon():
    """Retorna resposta vazia para requisições de favicon"""
    return Response(status_code=204)
=======
app.include_router(auth_router)

@app.get("/")
def root():
    return {"message": "JWT Protected API is running"}
>>>>>>> f634bdb28beaf0c91b110580539c4b8437841448
