from datetime import datetime
import os
import shutil
from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status
from fastapi.params import File, Form
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.employee_model import Employee
from app.schemas.employee_schema import EmployeeCreate, EmployeeResponse
from app.repositories.employee_repository import employee_repository
from app.services.employee_service import employee_service

router = APIRouter(prefix="/Employees", tags=["Employees"])


@router.get("/", response_model=List[EmployeeResponse])
def Get_All_Employee(
    skip: int = 0, 
    limit: int = 100,
    current_user: Employee = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all employees (Protected endpoint - requires authentication)

    This endpoint requires a valid JWT token in the Authorization header.
    """
    employees = employee_repository.get_all(db, skip=skip, limit=limit)
    return employees


@router.post("/AddOrEditEmployee", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def register(
    email: str = Form(...),
    CampusId: Optional[str] = Form(None),
    UserId: Optional[str] = Form(None),
    DesignationId: Optional[str] = Form(None),
    HireDate: Optional[str] = Form(None),
    Salary: Optional[str] = Form(None),
    IsHourlySalary: Optional[str] = Form(None),
    Experience: Optional[str] = Form(None),
    FullName: Optional[str] = Form(None),
    FatherName: Optional[str] = Form(None),
    Gender: Optional[str] = Form(None),
    DateOfBirth: Optional[str] = Form(None),
    CNIC: Optional[str] = Form(None),
    BloodGroup: Optional[str] = Form(None),
    MobileNo: Optional[str] = Form(None),
    PhoneNo: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    # Save uploaded file
    image_path = None
    if image:
        # Ensure the uploads folder exists
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True) # <- this creates the folder if it doesn't exist

        file_extension = os.path.splitext(image.filename)[1]
        filename = f"{uuid.uuid4()}{file_extension}"
        file_location = os.path.join(upload_dir, filename)

        with open(file_location, "wb") as f:
            shutil.copyfileobj(image.file, f)

        image_path = file_location

    # Create employee data
    user_data = EmployeeCreate(
        email=email,
        CampusId=CampusId,
        UserId=UserId,
        DesignationId=DesignationId,
        HireDate=HireDate,
        Salary=Salary,
        IsHourlySalary=IsHourlySalary,
        Experience=Experience,
        FullName=FullName,
        FatherName=FatherName,
        Gender=Gender,
        DateOfBirth=DateOfBirth,
        CNIC=CNIC,
        BloodGroup=BloodGroup,
        MobileNo=MobileNo,
        PhoneNo=PhoneNo,
        ImagePath=image_path,
        CreatedDate=datetime.utcnow(),  # Fixed
        CreatedBy=uuid.uuid4(),
        IsDeleted=False,
        Isactive=True
    )

    new_user = employee_service.register_user(db, user_data)
    if not new_user:
        raise HTTPException(status_code=400, detail="Employee registration failed")
    return new_user
