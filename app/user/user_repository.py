from sqlalchemy.orm import Session
from typing import Optional
from app.user.user_schema import User as UserSchema
from database.mysql_connection import SessionLocal
from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# MySQL 테이블 정의 (명세: 테이블 이름은 users) 
class UserORM(Base):
    __tablename__ = "users"
    email = Column(String(255), primary_key=True, index=True)
    password = Column(String(255))
    username = Column(String(255))

class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_user_by_email(self, email: str) -> Optional[UserSchema]:
        user = self.db.query(UserORM).filter(UserORM.email == email).first()
        return UserSchema(email=user.email, password=user.password, username=user.username) if user else None

    def save_user(self, user: UserSchema) -> UserSchema: 
        # 1. 기존에 해당 이메일을 가진 유저가 있는지 확인
        existing_user = self.db.query(UserORM).filter(UserORM.email == user.email).first()
        
        if existing_user:
            # 2. 이미 있다면 정보만 업데이트
            existing_user.password = user.password
            existing_user.username = user.username
        else:
            # 3. 없다면 새로 추가
            db_user = UserORM(email=user.email, password=user.password, username=user.username)
            self.db.add(db_user)
        
        self.db.commit()
        # self.db.refresh(existing_user if existing_user else db_user) # 필요시 사용
        return user

    def delete_user(self, user: UserSchema) -> UserSchema:
        db_user = self.db.query(UserORM).filter(UserORM.email == user.email).first()
        if db_user:
            self.db.delete(db_user)
            self.db.commit()
        return user