from fastapi import APIRouter
from fastapi import Request
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

with open("books.json", "r") as f:
    BOOK_LIST = json.load(f)

router = APIRouter(
    prefix="/api/v1",
    tags=["v1"],
)

@router.get("/books/top-rated")
async def get_books_top_rated():
    top_rated_books = []
    for book in BOOK_LIST:
        if book['rating'] == "Four" or book['rating']  == "Five":
            top_rated_books.append(book)
    return top_rated_books

@router.get("/books/price-range")
async def read_books_search(min: int = None, max: int = None):
    price_range =[]
    if  min == None or max == None:
            return {"error": "Sua busca não encontrou nenhum livro com este valor. Corrija os parametros Min e Max e tente novamente"}
    for book in BOOK_LIST:
        book_price = float(book["price"][2:])
        if  book_price >= min and book_price <= max:
            price_range.append(book)
    if len(price_range) == 0:
        return {"error": "Nenhum livro encontrado nessa faixa de preço."}
    else:
        return price_range
       
@router.get("/books/search")
async def read_books_search(request: Request, title: str = None, category: str = None):
    book_list = BOOK_LIST
    book_list_searched = []

    if title is not None and category is not None:
        for book in book_list:
            if book["title"] == title and book["category"] == category:
                book_list_searched.append(book)
        client_ip = request.client.host
        logger.info(
            f"Busca por titulo - {title} -  e categoria - {category} - realizada por {client_ip}"
        )
        return book_list_searched

    elif title is not None:
        for book in book_list:
            if book["title"] == title:
                book_list_searched.append(book)
        client_ip = request.client.host
        logger.info(f"Busca por titulo - {title} - realizada por {client_ip}")
        return book_list_searched

    elif category is not None:
        for book in book_list:
            if book["category"] == category:
                book_list_searched.append(book)
        client_ip = request.client.host
        logger.info(f"Busca por categoria - {category} - realizada por {client_ip}")
        return book_list_searched

    if title is None and category is None:
        client_ip = request.client.host
        logger.info(
            f"Busca invalida - sem titulo ou categoria -  realizada por {client_ip}"
        )
        return "Categoria ou ID necessario para processar busca"

    else:
        client_ip = request.client.host
        logger.info(
            f"Busca possui erros e nenhum livro foi encontrado - realizada por {client_ip}"
        )
        return {"error": "Book not found"}


@router.get("/books/{id}")
async def read_books_id(id: int, request: Request):
    for book in BOOK_LIST:
        if book["id"] == id:
            client_ip = request.client.host
            logger.info(f"Busca por id - {id} -  realizada por {client_ip}")
            return book
    else:
        return {"error": "Book not found"}


@router.get("/books")
async def read_books(request: Request):
    book_list_titles = []
    for book_title in BOOK_LIST:
        book_list_titles.append(book_title["title"])
    client_ip = request.client.host
    logger.info(f"Busca geral realizada por {client_ip}")
    return book_list_titles


@router.get("/categories")
async def read_book_categories(request: Request):
    book_categories = []
    for book in BOOK_LIST:
        book_categories.append(book["category"])
    client_ip = request.client.host
    logger.info(f"Busca geral por categoria  -  realizada por {client_ip}")
    return book_categories


@router.get("/health")
async def read_api_health(request: Request):
    pass
