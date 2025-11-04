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


### create books. protegido por JWT ####
@router.post("/books", 
    responses={
        201: {"description": "Livro inserido com sucesso."},
        401: {"description": "Authentication required"},
        409: {"description": "Já existe um livro com esse ID"},
        500: {"description": "Internal server error"}
    },
    summary="Insere um novo livro",
    description="Insere um livro na coleção. Requires JWT authentication.",
    status_code=201
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
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            raise HTTPException(status_code=409, detail="Já existe um livro com esse ID")
        logger.error(f"Error creating book: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


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


##### buscar books por categoria e/ou title ########
@router.get("/books/search")
async def read_books_search(
    request: Request,
    title: str = None,
    category: str = None,
):
    if not title and not category:
        raise HTTPException(status_code=400, detail="Categoria ou titulo necessario para processar busca")
    
    try:
        filter_parts = []
        expr_values = {}
        
        if title:
            filter_parts.append("contains(#title, :title)")
            expr_values[':title'] = title
        
        if category:
            filter_parts.append("#category = :category")
            expr_values[':category'] = category
        
        response = table.scan(
            FilterExpression=' AND '.join(filter_parts),
            ExpressionAttributeNames={
                '#title': 'title',
                '#category': 'category'
            },
            ExpressionAttributeValues=expr_values
        )
        
        logger.info(f"Search title={title} category={category}")
        return response.get('Items', [])
    
    except ClientError as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


##### get books by id #########
@router.get("/books/{id}")
async def read_books_id(id: int, request: Request):
    try:
        response = table.get_item(Key={'id': id})
        item = response.get('Item')

        if not item:
            raise HTTPException(status_code=404, detail="Book not found")

        logger.info(f"Busca por id={id} realizada por {request.client.host}")
        return item

    except ClientError as e:
        logger.error(f"DynamoDB error: {e.response['Error']['Message']}")
        raise HTTPException(status_code=500, detail=e.response['Error']['Message'])

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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


######## health check #######
@router.get("/health")
async def read_api_health():
    return {"status": "ok"}