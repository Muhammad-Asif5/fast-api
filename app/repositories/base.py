from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy import String
from sqlalchemy.orm import Session
from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    def get_by_id(self, db: Session, id: int):
        primary_key = list(self.model.__table__.primary_key.columns)[0]
        return db.query(self.model).filter(primary_key == id, self.model.IsDeleted == False).first()
    
    def get_by_cnic(self, db: Session, cnic: str):
        return db.query(self.model).filter(
            self.model.CNIC == cnic,
            self.model.IsDeleted == False
        ).first()

    def get_by_email(self, db: Session, email: str):
        return db.query(self.model).filter(
            self.model.Email == email,
            self.model.IsDeleted == False
        ).first()
    
    def get_by_duplicate_email(self, db: Session, email: str, employeeId: int):
        return db.query(self.model).filter(
            self.model.Email == email,
            self.model.EmployeeId != employeeId,
            self.model.IsDeleted == False
        ).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100, order_by: str = "id") -> List[ModelType]:
        # SQL Server requires ORDER BY when using OFFSET/LIMIT
        return db.query(self.model).order_by(getattr(self.model, order_by)).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: dict) -> ModelType:
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, id: int, obj_in: dict) -> Optional[ModelType]:
        db_obj = self.get_by_id(db, id)
        if db_obj:
            for key, value in obj_in.items():
                setattr(db_obj, key, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        db_obj = self.get_by_id(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False