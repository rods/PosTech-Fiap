from fastapi import FastAPI
from .routers import books,insights
from app.routers.auth import router as auth_router
from app.models.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="JWT Protected API")

app.include_router(books.router)
app.include_router(insights.router)
app.include_router(auth_router)

@app.get("/")
def root():
    return {"message": "JWT Protected API is running"}