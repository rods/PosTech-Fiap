from fastapi import FastAPI
from fastapi.responses import Response
from .routers import books, insights, users, ml
from .internal.training_data import train_recommendation_model
import boto3 
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

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
app.include_router(users.router)
app.include_router(ml.router)

@app.get("/favicon.ico")
async def favicon():
    """Retorna resposta vazia para requisições de favicon"""
    return Response(status_code=204)
