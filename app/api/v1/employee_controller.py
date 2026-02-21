from datetime import datetime
import os
from typing import List, Optional
from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status
from fastapi.params import File
from sqlalchemy.orm import Session
from pydantic import ValidationError

from app.core.database import get_db
from app.core.response import success_response
from app.core.security import get_current_active_user
from app.models.employee_model import Employee
from app.schemas.employee_schema import EmployeeCreate, EmployeeResponse
from app.repositories.employee_repository import employee_repository
from app.services.employee_service import employee_service
import uuid
from uuid import UUID
from app.common import parse_date, validate_image_file, save_uploaded_file

router = APIRouter(prefix="/Employees", tags=["Employees"])

# Configuration

@router.get("/", response_model=List[EmployeeResponse])
def get_all_employees(
    skip: int = 0, 
    limit: int = 100,
    # current_user: Employee = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all employees (Protected endpoint - requires authentication)

    This endpoint requires a valid JWT token in the Authorization header.
    
    Parameters:
    - skip: Number of records to skip (pagination)
    - limit: Maximum number of records to return (max: 100)
    """
    
    if limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be between 1 and 100"
        )
    
    employees = employee_repository.get_all(db, skip=skip, limit=limit)
    # Convert ORM objects to Pydantic schemas
    employees_schema = [EmployeeResponse.model_validate(emp) for emp in employees]
     # If DB may contain invalid data, use model_construct() instead
     
    return success_response(
        data=employees_schema,
        message=f"{len(employees_schema)} employee(s) retrieved",
        status_code=status.HTTP_200_OK
    )

@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(
    employee_id: int,
    current_user: Employee = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific employee by ID"""
    employee = employee_repository.get_by_id(db, employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found"
        )
    return employee


@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(
    Email: str = Form(...),
    CampusId: int = Form(...),
    DesignationId: int = Form(...),
    FullName: str = Form(...),
    FatherName: str = Form(...),
    Gender: str = Form(...),
    DateOfBirth: str = Form(...),
    CNIC: str = Form(...),
    PhoneNo: str = Form(...),
    UserId: UUID = Form(...),
    HireDate: Optional[str] = Form(None),
    Salary: Optional[float] = Form(None),
    IsHourlySalary: Optional[bool] = Form(False),
    Experience: Optional[int] = Form(None),
    BloodGroup: Optional[str] = Form(None),
    MobileNo: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    current_user: Employee = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new employee with comprehensive validation
    
    Required fields:
    - UserId: UUID of the user creating the employee (optional, will be generated if not provided)
    - email: Valid email address
    - CampusId: Campus identifier (positive integer)
    - DesignationId: Designation identifier (positive integer)
    - FullName: Employee's full name
    - FatherName: Father's name
    - Gender: Male/Female/Other
    - DateOfBirth: Format YYYY-MM-DD (must be 18+ years old)
    - CNIC: National ID (13 digits)
    - PhoneNo: Contact phone number
    
    Optional fields:
    - image: Profile image (JPG, PNG, GIF, WEBP - max 5MB)
    - HireDate, Salary, Experience, BloodGroup, MobileNo, etc.
    """
     
    raw_data = {
        "Email": Email,
        "CampusId": CampusId,
        "DesignationId": DesignationId,
        "FullName": FullName,
        "FatherName": FatherName,
        "Gender": Gender,
        "DateOfBirth": DateOfBirth,
        "HireDate": HireDate,
        "CNIC": CNIC,
        "PhoneNo": PhoneNo,
        "MobileNo": MobileNo,
        "BloodGroup": BloodGroup,
        "Salary": Salary,
        "IsHourlySalary": IsHourlySalary,
        "Experience": Experience,
        "UserId": UserId
    }

    return employee_service.create_employee(
        db=db,
        raw_data=raw_data,
        image=image,
        current_user=current_user
    )


@router.put("/{employeeId}", response_model=EmployeeResponse)
def update_employee(
    employeeId: int,
    Email: Optional[str] = Form(None),
    CampusId: Optional[int] = Form(None),
    DesignationId: Optional[int] = Form(None),
    FullName: Optional[str] = Form(None),
    FatherName: Optional[str] = Form(None),
    Gender: Optional[str] = Form(None),
    DateOfBirth: Optional[str] = Form(None),
    CNIC: Optional[str] = Form(None),
    PhoneNo: Optional[str] = Form(None),
    Salary: Optional[float] = Form(None),
    IsHourlySalary: Optional[bool] = Form(None),
    Experience: Optional[int] = Form(None),
    BloodGroup: Optional[str] = Form(None),
    MobileNo: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    current_user: Employee = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):

    update_data = {
        "Email": Email,
        "CampusId": CampusId,
        "DesignationId": DesignationId,
        "FullName": FullName,
        "FatherName": FatherName,
        "Gender": Gender,
        "DateOfBirth": DateOfBirth,
        "CNIC": CNIC,
        "PhoneNo": PhoneNo,
        "Salary": Salary,
        "IsHourlySalary": IsHourlySalary,
        "Experience": Experience,
        "BloodGroup": BloodGroup,
        "MobileNo": MobileNo
    }

    return employee_service.update_employee(
        db=db,
        employee_id=employeeId,
        update_fields=update_data,
        image=image,
        current_user=current_user
    )

@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(
    employee_id: int,
    current_user: Employee = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Soft delete an employee"""
    employee = employee_repository.get_by_id(db, employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found"
        )
    
    employee.IsDeleted = True
    employee.Isactive = False
    db.commit()
    
    return None