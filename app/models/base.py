from sqlalchemy import Column, DateTime, Boolean, text
from sqlalchemy.sql import func
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from app.core.database import Base


class BaseModel(Base):
    __abstract__ = True
    
    CreatedDate = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    CreatedBy = Column(UNIQUEIDENTIFIER, nullable=False)
    ModifiedDate = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)
    ModifiedBy = Column(UNIQUEIDENTIFIER, nullable=True)
    IsDeleted = Column(Boolean, server_default=text("0"), nullable=False)
    Isactive = Column(Boolean, server_default=text("1"), nullable=False)