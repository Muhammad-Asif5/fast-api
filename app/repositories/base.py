from typing import Generic, TypeVar, Type, Optional, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from app.core.database import Base


ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model
        
    # ---------------------------------------------------------
    # Internal Base Query (Soft Delete Safe)
    # ---------------------------------------------------------

    def _base_query(self, db: Session):
        """
        Base query that automatically filters soft-deleted records
        """
        if hasattr(self.model, "IsDeleted"):
            return db.query(self.model).filter(self.model.IsDeleted == False)
        return db.query(self.model)

    @property
    def _pk_column(self):
        return list(self.model.__table__.primary_key.columns)[0]
    
    # ---------------------------------------------------------
    # Get By ID
    # ---------------------------------------------------------

    def get_by_id(self, db: Session, id: Any) -> Optional[ModelType]:
        primary_key = list(self.model.__table__.primary_key.columns)[0]

        query = self._base_query(db).filter(primary_key == id)

        return query.first()

    # ---------------------------------------------------------
    # Get All (Pagination Safe for SQL Server)
    # ---------------------------------------------------------

    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None
    ) -> List[ModelType]:

        query = self._base_query(db)

        # SQL Server requires ORDER BY when using OFFSET
        if order_by and hasattr(self.model, order_by):
            query = query.order_by(getattr(self.model, order_by))
        else:
            # Default order by primary key
            primary_key = list(self.model.__table__.primary_key.columns)[0]
            query = query.order_by(primary_key)

        return query.offset(skip).limit(limit).all()

    # ---------------------------------------------------------
    # Create
    # ---------------------------------------------------------

    def create(
        self,
        db: Session,
        obj_in: dict
    ) -> ModelType:

        try:
            db_obj = self.model(**obj_in)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj

        except SQLAlchemyError as e:
            db.rollback()
            raise e

    # ---------------------------------------------------------
    # Update
    # ---------------------------------------------------------

    def update(
        self,
        db: Session,
        id: Any,
        obj_in: dict
    ) -> Optional[ModelType]:

        db_obj = self.get_by_id(db, id)

        if not db_obj:
            return None

        try:
            for key, value in obj_in.items():
                setattr(db_obj, key, value)

            db.commit()
            db.refresh(db_obj)
            return db_obj

        except SQLAlchemyError as e:
            db.rollback()
            raise e

    # ---------------------------------------------------------
    # Hard Delete (Use Carefully)
    # ---------------------------------------------------------

    def delete(
        self,
        db: Session,
        id: Any
    ) -> bool:

        db_obj = self.get_by_id(db, id)

        if not db_obj:
            return False

        try:
            db.delete(db_obj)
            db.commit()
            return True

        except SQLAlchemyError as e:
            db.rollback()
            raise e

    # ---------------------------------------------------------
    # Soft Delete (Enterprise Safe)
    # ---------------------------------------------------------

    def soft_delete(
        self,
        db: Session,
        id: Any
    ) -> bool:

        db_obj = self.get_by_id(db, id)

        if not db_obj:
            return False

        if not hasattr(db_obj, "IsDeleted"):
            raise AttributeError("Model does not support soft delete")

        try:
            db_obj.IsDeleted = True

            if hasattr(db_obj, "IsActive"):
                db_obj.IsActive = False

            db.commit()
            return True

        except SQLAlchemyError as e:
            db.rollback()
            raise e

    # ---------------------------------------------------------
    # Exists (SQL Server Safe)
    # ---------------------------------------------------------

    def exists(self, db: Session, **filters) -> bool:
        """
        SQL Server safe exists check.
        Example:
            repo.exists(db, Email="test@test.com")
        """

        query = self._base_query(db)

        for attr, value in filters.items():
            if hasattr(self.model, attr):
                query = query.filter(getattr(self.model, attr) == value)

        return query.first() is not None
