from sqlalchemy import Column, String, Integer, DateTime, Boolean, text, Numeric,CheckConstraint,UniqueConstraint,Index,Enum
from sqlalchemy.sql import func
from app.common import GenderEnum
from app.models.base import BaseModel
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER

class Employee(BaseModel):
    __primary_key__ = "EmployeeId",
    __tablename__ = "Employees"
    __table_args__ = (
        UniqueConstraint("CNIC", name="uq_employee_cnic"),
        UniqueConstraint("Email", name="uq_employee_email"),
        CheckConstraint("Salary >= 0", name="ck_salary_positive"),
        CheckConstraint("Experience >= 0", name="ck_experience_positive"),
        {"schema": "academic"},
    )

    EmployeeId = Column(Integer, primary_key=True, index=True, autoincrement=True)
    CampusId = Column(Integer, index=True, nullable=False,)
    UserId = Column(UNIQUEIDENTIFIER, unique=True, index=True, nullable=True)
    DesignationId = Column(Integer, index=True, nullable=False)
    HireDate = Column(DateTime, nullable=True, server_default=func.now())
    Salary = Column(Numeric(18, 2), nullable=True)
    IsHourlySalary = Column(Boolean, nullable=False, server_default=text("0"))
    Experience = Column(Integer, nullable=True)
    FullName = Column(String(100),  index=True, nullable=False)
    FatherName = Column(String(100), nullable=False)
    Gender = Column(Enum(GenderEnum), nullable=False)
    DateOfBirth = Column(DateTime, nullable=False)
    CNIC = Column(String(15), nullable=False, index=True)
    BloodGroup = Column(String(5), nullable=True)
    MobileNo = Column(String(15), nullable=True)
    PhoneNo = Column(String(15), nullable=False)
    Email = Column(String(255), nullable=False, index=True)
    ImagePath = Column(String(1000), nullable=True) 
    
     # Performance Indexes
    __table_args__ = (
        UniqueConstraint("CNIC", name="uq_employee_cnic"),
        UniqueConstraint("Email", name="uq_employee_email"),
        Index("ix_employee_campus_designation", "CampusId", "DesignationId"),
        {"schema": "academic"},
    )
