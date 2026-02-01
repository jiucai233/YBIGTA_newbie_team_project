from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

from app.user.user_router import user
from app.review.review_router import router as review_router
from app.user.user_repository import Base
from database.mysql_connection import engine

Base.metadata.create_all(bind=engine)
app = FastAPI()

static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

app.include_router(user, tags=["User"])
app.include_router(review_router, tags=["Review"])

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)