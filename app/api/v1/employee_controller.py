from datetime import datetime
import os
import shutil
from typing import List, Optional
from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status
from fastapi.params import File
from sqlalchemy.orm import Session
from pydantic import ValidationError

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.employee_model import Employee
from app.schemas.employee_schema import EmployeeCreate, EmployeeResponse
from app.repositories.employee_repository import employee_repository
from app.services.employee_service import employee_service
import uuid
from uuid import UUID

router = APIRouter(prefix="/Employees", tags=["Employees"])

# Configuration
UPLOAD_DIR = "uploads/employees"
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def validate_image_file(file: UploadFile) -> None:
    """Validate uploaded image file"""
    if not file:
        return
    
    # Check file extension
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
        )
    
    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()  # Get position (file size)
    file.file.seek(0)  # Reset to beginning
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024)}MB"
        )
    
    # Validate MIME type
    content_type = file.content_type
    if content_type not in ['image/jpeg', 'image/png', 'image/gif', 'image/webp']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image format"
        )


def save_uploaded_file(file: UploadFile) -> str:
    """Save uploaded file and return path"""
    # Ensure the uploads folder exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1].lower()
    filename = f"{uuid.uuid4()}{file_extension}"
    file_location = os.path.join(UPLOAD_DIR, filename)
    
    try:
        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)
        return file_location
    except Exception as e:
        # Clean up if save fails
        if os.path.exists(file_location):
            os.remove(file_location)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )


@router.get("/", response_model=List[EmployeeResponse])
def get_all_employees(
    skip: int = 0, 
    limit: int = 100,
    current_user: Employee = Depends(get_current_active_user),
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
            detail="Limit cannot exceed 100"
        )
    
    employees = employee_repository.get_all(db, skip=skip, limit=limit)
    return employees


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
    email: str = Form(...),
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
    
    # Validate and save image if provided
    image_path = None
    if image and image.filename:
        try:
            validate_image_file(image)
            image_path = save_uploaded_file(image)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Image upload failed: {str(e)}"
            )
    
    try:
        # Parse and validate dates
        from datetime import datetime
        date_of_birth = datetime.fromisoformat(DateOfBirth).date() if DateOfBirth else None
        hire_date = datetime.fromisoformat(HireDate).date() if HireDate else None
        
        # Create employee data with Pydantic validation
        employee_data = EmployeeCreate(
            email=email,
            CampusId=CampusId,
            UserId=UserId,
            DesignationId=DesignationId,
            HireDate=hire_date,
            Salary=Salary,
            IsHourlySalary=IsHourlySalary,
            Experience=Experience,
            FullName=FullName,
            FatherName=FatherName,
            Gender=Gender,
            DateOfBirth=date_of_birth,
            CNIC=CNIC,
            BloodGroup=BloodGroup,
            MobileNo=MobileNo,
            PhoneNo=PhoneNo,
            ImagePath=image_path,
            CreatedDate=datetime.utcnow(),
            CreatedBy=current_user.EmployeeId if hasattr(current_user, 'EmployeeId') else uuid.uuid4(),
            IsDeleted=False,
            Isactive=True
        )
    except ValueError as e:
        # Clean up uploaded image if validation fails
        if image_path and os.path.exists(image_path):
            os.remove(image_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid date format: {str(e)}"
        )
    except ValidationError as e:
        # Clean up uploaded image if validation fails
        if image_path and os.path.exists(image_path):
            os.remove(image_path)
        
        # Format validation errors
        errors = []
        for error in e.errors():
            field = ' -> '.join(str(loc) for loc in error['loc'])
            errors.append(f"{field}: {error['msg']}")
        
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Validation failed",
                "errors": errors
            }
        )
    
    try:
        # Check for duplicate UserId if provided
        existing_user = db.query(Employee).filter(
            Employee.UserId == employee_data.UserId,
            Employee.IsDeleted == False
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Username ({UserId}) already registered"
            )
        
        # Check for duplicate CNIC
        existing_employee = db.query(Employee).filter(
            Employee.CNIC == employee_data.CNIC,
            Employee.IsDeleted == False
        ).first()
        
        if existing_employee:
            # Clean up uploaded image
            if image_path and os.path.exists(image_path):
                os.remove(image_path)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Employee with this CNIC already exists"
            )
        
        # Check for duplicate email
        existing_email = db.query(Employee).filter(
            Employee.Email == employee_data.email,
            Employee.IsDeleted == False
        ).first()
        
        if existing_email:
            # Clean up uploaded image
            if image_path and os.path.exists(image_path):
                os.remove(image_path)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Employee with this email already exists"
            )
        
        # Create employee
        new_employee = employee_service.register_user(db, employee_data)
        if not new_employee:
            # Clean up uploaded image
            if image_path and os.path.exists(image_path):
                os.remove(image_path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Employee registration failed"
            )
        
        return new_employee
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up uploaded image on any error
        if image_path and os.path.exists(image_path):
            os.remove(image_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create employee: {str(e)}"
        )


@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: int,
    email: Optional[str] = Form(None),
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
    """Update an existing employee"""
    # Get existing employee
    existing_employee = employee_repository.get_by_id(db, employee_id)
    if not existing_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found"
        )
    
    # Handle image upload if provided
    image_path = existing_employee.ImagePath
    if image and image.filename:
        validate_image_file(image)
        # Delete old image if exists
        if existing_employee.ImagePath and os.path.exists(existing_employee.ImagePath):
            os.remove(existing_employee.ImagePath)
        image_path = save_uploaded_file(image)
    
    # Update fields
    update_data = {}
    if email is not None:
        update_data['Email'] = email
    if CampusId is not None:
        update_data['CampusId'] = CampusId
    if DesignationId is not None:
        update_data['DesignationId'] = DesignationId
    if FullName is not None:
        update_data['FullName'] = FullName
    if FatherName is not None:
        update_data['FatherName'] = FatherName
    if Gender is not None:
        update_data['Gender'] = Gender
    if PhoneNo is not None:
        update_data['PhoneNo'] = PhoneNo
    if Salary is not None:
        update_data['Salary'] = Salary
    if Experience is not None:
        update_data['Experience'] = Experience
    if image_path:
        update_data['ImagePath'] = image_path
    
    # Apply updates
    for key, value in update_data.items():
        setattr(existing_employee, key, value)
    
    db.commit()
    db.refresh(existing_employee)
    
    return existing_employee


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