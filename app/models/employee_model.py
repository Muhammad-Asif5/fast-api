from sqlalchemy import Column, String, Integer, DateTime, Boolean, text, Numeric
from sqlalchemy.sql import func
from app.models.base import BaseModel
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER

class Employee(BaseModel):
    __tablename__ = "Employees"
    __table_args__ = {"schema": "academic"}  # SQL Server schema - MUST BE UNCOMMENTED
    
    EmployeeId = Column(Integer, primary_key=True, index=True, autoincrement=True)
    CampusId = Column(Integer, index=True, nullable=False,)
    UserId = Column(UNIQUEIDENTIFIER, unique=True, index=True, nullable=True)
    DesignationId = Column(Integer, index=True, nullable=False)
    HireDate = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    Salary = Column(Numeric(18, 2, asdecimal=True), nullable=True)
    IsHourlySalary = Column(Boolean, server_default=text("0"), nullable=True)
    Experience = Column(Integer, index=True, nullable=True)
    FullName = Column(String(100),  index=True, nullable=False)
    FatherName = Column(String(100), index=True, nullable=False)
    Gender = Column(String(10), index=True, nullable=False)
    DateOfBirth = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    CNIC = Column(String(15), index=True, nullable=False)
    BloodGroup = Column(String(13), index=True, nullable=True)
    MobileNo = Column(String(15), index=True, nullable=True)
    PhoneNo = Column(String(15), index=True, nullable=False)
    Email = Column(String(100), index=True, nullable=False)
    ImagePath = Column(String(1000), nullable=True) 
    