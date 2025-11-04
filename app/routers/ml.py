from fastapi import APIRouter, Request, Query
import json
import logging
from app.internal.training_data import train_recommendation_model
import pickle
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar lista de livros com tratamento de erro
try:
    with open("books.json", "r") as f:
        BOOK_LIST = json.load(f)
    logger.info("books.json carregado com sucesso")
except FileNotFoundError:
    logger.error("Arquivo books.json não encontrado")
    BOOK_LIST = []
except json.JSONDecodeError:
    logger.error("Erro ao decodificar books.json")
    BOOK_LIST = []

# Carregar modelo com tratamento de erro
try:
    with open("model.pkl", "rb") as m:
        model = pickle.load(m)
    logger.info("model.pkl carregado com sucesso")
except FileNotFoundError:
    logger.error("Arquivo model.pkl não encontrado. Execute o treinamento primeiro.")
    model = None
except Exception as e:
    logger.error(f"Erro ao carregar model.pkl: {e}")
    model = None

router = APIRouter(
    prefix="/api/v1",
    tags=["v1"],
)

# Mapa de categorias como constante global
CATEGORY_MAP = {
    "Poetry": 0,
    "Historical Fiction": 1,
    "Fiction": 2,
    "Mystery": 3,
    "History": 4,
    "Young Adult": 5,
    "Business": 6,
    "Default": 7,
    "Science Fiction": 8,
    "Politics": 9,
    "Travel": 10,
    "Thriller": 11,
    "Music": 12,
    "Food and Drink": 13,
    "Romance": 14,
    "Childrens": 15,
    "Nonfiction": 16,
    "Art": 17,
    "Spirituality": 18,
    "Philosophy": 19,
    "Sequential Art": 20
}

@router.get("/ml/features")
async def get_ml_features():
    if not BOOK_LIST:
        logger.error("BOOK_LIST está vazio")
        return {"error": "Nenhum livro disponível"}
    
    feature_data = []
    for book in BOOK_LIST:
        book_category = book.get("category")
        
        # Verifica se a categoria existe no mapa
        if book_category not in CATEGORY_MAP:
            logger.warning(f"Categoria '{book_category}' não encontrada no mapa")
            continue
        
        feature_data.append({
            "title": book["title"],
            "category": book_category,
            "category_feature": CATEGORY_MAP[book_category],
        })
    
    logger.info(f"Retornando {len(feature_data)} features")
    return {"Features": feature_data}

def get_rating_value(rating_text):
    """Converte rating de texto para número para comparação"""
    rating_map = {
        "One": 1,
        "Two": 2, 
        "Three": 3,
        "Four": 4,
        "Five": 5
    }
    return rating_map.get(rating_text, 0)

@router.post("/ml/predictions")
async def recommend_books(book_title: str = Query(...)):
    
    # Verifica se o modelo está carregado
    if model is None:
        logger.error("Modelo não está carregado")
        return {"error": "Modelo não disponível. Execute o treinamento primeiro."}
    
    if not BOOK_LIST:
        logger.error("BOOK_LIST está vazio")
        return {"error": "Nenhum livro disponível"}
    
    # Buscar o livro
    book_found = None
    for book in BOOK_LIST:
        if book["title"].lower() == book_title.lower():
            book_found = book
            break
    
    if not book_found:
        logger.warning(f"Livro '{book_title}' não encontrado")
        return {"error": "Livro não encontrado"}
    
    # Verificar se a categoria existe no mapa
    book_category = book_found.get("category")
    if book_category not in CATEGORY_MAP:
        logger.error(f"Categoria '{book_category}' não encontrada no mapa")
        return {"error": "Categoria do livro não reconhecida"}
    
    book_category_number = CATEGORY_MAP[book_category]
    book_rating = book_found.get("rating")
    book_rating_value = get_rating_value(book_rating)
    
    # Pedir ao modelo livros similares
    try:
        distances, indices = model.kneighbors([[book_category_number]])
    except Exception as e:
        logger.error(f"Erro ao buscar recomendações: {e}")
        return {"error": "Erro ao gerar recomendações"}
    
    # Filtrar recomendações por rating similar ou igual
    recommendations = []
    for i in indices[0]:
        candidate_book = BOOK_LIST[i]
        
        # Pula o próprio livro
        if candidate_book["title"] == book_found["title"]:
            continue
            
        candidate_rating_value = get_rating_value(candidate_book.get("rating"))
        
        # Só recomenda se o rating for similar ou igual (diferença máxima de 1)
        if abs(candidate_rating_value - book_rating_value) <= 1:
            recommendations.append({
                "title": candidate_book["title"],
                "category": candidate_book["category"],
                "rating": candidate_book["rating"],
                "price": candidate_book["price"]
            })
        
        # Limita a 5 recomendações
        if len(recommendations) >= 5:
            break
    
    logger.info(f"Retornando {len(recommendations)} recomendações para '{book_title}' com rating similar")
    return {
        "input_book": {
            "title": book_found["title"],
            "rating": book_found["rating"],
            "price": book_found["price"]
        },
        "recommendations": recommendations,
        "filter_criteria": f"Rating similar ou igual a '{book_rating}'"
    }
