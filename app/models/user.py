from sqlalchemy import Column, String
from app.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"
    __table_args__ = {"schema": "dbo"}  # SQL Server schema - MUST BE UNCOMMENTED
    
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)