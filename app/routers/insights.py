from fastapi import APIRouter
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

@router.get("/stats/overview")
async def get_stats():
    total_price = 0
    for book in BOOK_LIST:
        book_price = float(book["price"][2:])
        total_price = total_price + book_price
    total_books = len(BOOK_LIST)
    mean_price = round(total_price / total_books)
    return {
        "total_books": total_books,
        "total_price": total_price,
        "mean_price": mean_price,
    }

@router.get("/stats/categories")
async def get_stats_categories():
    categories = []
    book_price = 0
    avg_book_price = {}

    for book in BOOK_LIST:
        book_category = book["category"]
        categories.append(book_category)

    unique_categories = list(set(categories))
    category_results = {}

    for category in unique_categories:
        books_in_category = []
        total_book_price = {}
        total_book_price[category] = 0
        for book in BOOK_LIST:
            if book["category"] == category:
                book_price = float(book["price"][2:])
                books_in_category.append(book)
                total_book_price[category] = total_book_price[category] + book_price
        avg_book_price[category] = round(
            total_book_price[category] / len(books_in_category), 2
        )
        category_results[category] = len(books_in_category)  
    return category_results, avg_book_price  
