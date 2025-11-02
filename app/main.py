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
    return {"message": "PosTech FIAP Book Recommendation API is running"}

@app.get("/favicon.ico")
async def favicon():
    """Retorna resposta vazia para requisições de favicon"""
    return Response(status_code=204)
