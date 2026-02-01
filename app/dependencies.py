from fastapi import Depends
from sqlalchemy.orm import Session
from app.user.user_repository import UserRepository
from app.user.user_service import UserService
from database.mysql_connection import SessionLocal

# DB 세션을 생성하고 닫아주는 제너레이터
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

def get_user_service(repo: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repo)