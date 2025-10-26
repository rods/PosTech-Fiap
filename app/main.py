from fastapi import FastAPI
from .routers import books,insights

app = FastAPI()

app.include_router(books.router)
app.include_router(insights.router)