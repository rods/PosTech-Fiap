from fastapi import APIRouter, Request, Depends, HTTPException, status
from pydantic import BaseModel
import boto3
import logging
from decimal import Decimal
from app.core.auth import get_current_user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('Books')

class Book(BaseModel):
    id: int
    title: str
    price: float
    rating: int
    availability: str
    category: str

def get_all_books():
    response = table.scan()
    return response.get('Items', [])

router = APIRouter(
    prefix="/api/v1",
    tags=["v1"],
)

@router.post("/books", 
    responses={
        201: {"description": "Livro inserido com sucesso"},
        401: {"description": "Authentication required"},
        409: {"description": "Já existe um livro com esse ID"},
        500: {"description": "Internal server error"}
    },
    summary="Insere um novo livro",
    description="Insere um livro na coleção. Requires JWT authentication."
)
async def create_book(
    book: Book, 
    request: Request,
    current_user = Depends(get_current_user)
):

    try:
        table.put_item(
            Item={
                'id': book.id,
                'title': book.title,
                'price': Decimal(str(book.price)),
                'rating': book.rating,
                'availability': book.availability,
                'category': book.category
            },
            ConditionExpression='attribute_not_exists(id)'
        )
        logger.info(f"Book {book.id} created by user {current_user.username} from {request.client.host}")
        return {
            "message": "Livro criado com sucesso", 
            "id": book.id,
            "created_by": current_user.username
        }
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        logger.warning(f"Attempt to create duplicate book ID {book.id} by user {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Book with ID {book.id} already exists"
        )
    except Exception as e:
        logger.error(f"Error creating book {book.id} by user {current_user.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while creating book"
        )

@router.get("/books/top-rated")
async def get_books_top_rated():
    books = get_all_books()
    return [b for b in books if b['rating'] >= 4]

@router.get("/books/price-range")
async def read_books_search(min: int = None, max: int = None):
    if min is None or max is None:
        return {"error": "Sua busca não encontrou nenhum livro com este valor. Corrija os parametros Min e Max e tente novamente"}
    
    books = get_all_books()
    price_range = [b for b in books if min <= float(b['price']) <= max]
    
    if not price_range:
        return {"error": "Nenhum livro encontrado nessa faixa de preço."}
    return price_range
       
@router.get("/books/search")
async def read_books_search(request: Request, title: str = None, category: str = None):
    books = get_all_books()
    client_ip = request.client.host
    
    if title and category:
        result = [b for b in books if b['title'] == title and b['category'] == category]
        logger.info(f"Busca por titulo - {title} - e categoria - {category} - realizada por {client_ip}")
        return result
    elif title:
        result = [b for b in books if b['title'] == title]
        logger.info(f"Busca por titulo - {title} - realizada por {client_ip}")
        return result
    elif category:
        result = [b for b in books if b['category'] == category]
        logger.info(f"Busca por categoria - {category} - realizada por {client_ip}")
        return result
    
    logger.info(f"Busca invalida - sem titulo ou categoria - realizada por {client_ip}")
    return {"error": "Categoria ou titulo necessario para processar busca"}

@router.get("/books/{id}")
async def read_books_id(id: str, request: Request):
    try:
        response = table.get_item(Key={'id': id})
        item = response.get('Item')
        if not item:
            raise HTTPException(status_code=404, detail="Book not found")

        logger.info(f"Busca por id={id} realizada por {request.client.host}")
        return item

    except ClientError as e:
        logger.error(f"DynamoDB error: {e.response['Error']['Message']}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error")

@router.get("/books")
async def read_books(request: Request):
    books = get_all_books()
    logger.info(f"Busca geral realizada por {request.client.host}")
    return [b['title'] for b in books]

@router.get("/categories")
async def read_book_categories(request: Request):
    books = get_all_books()
    logger.info(f"Busca geral por categoria - realizada por {request.client.host}")
    return list(set(b['category'] for b in books))


@router.get("/health")
async def read_api_health(request: Request):
    pass
