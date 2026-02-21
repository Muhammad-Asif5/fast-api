from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from typing import Optional, Union
from uuid import UUID
from datetime import datetime, date
import re

class EmployeeResponse(BaseModel):
    EmployeeId: int
    CreatedBy: Optional[UUID] = None
    IsActive: bool = Field(alias="IsActive")
    CreatedDate: datetime
    FullName: str
    FatherName: str
    Gender: str
    DateOfBirth: datetime
    CNIC: str
    BloodGroup: Optional[str] = None
    MobileNo: Optional[str] = None
    PhoneNo: str
    Email: EmailStr
    ImagePath: Optional[str] = None
    CampusId: int
    DesignationId: int
    HireDate: Optional[datetime] = None
    Salary: Optional[float] = None
    Experience: Optional[int] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class EmployeeCreate(BaseModel):
    # Required fields
    Email: EmailStr = Field(..., description="Valid email address")
    CampusId: int = Field(..., gt=0, description="Campus ID must be positive")
    DesignationId: int = Field(..., gt=0, description="Designation ID must be positive")
    FullName: str = Field(..., min_length=2, max_length=100, description="Full name required")
    FatherName: str = Field(..., min_length=2, max_length=100, description="Father's name required")
    Gender: str = Field(..., description="Gender (Male/Female/Other)")
    DateOfBirth: Union[datetime, date] = Field(..., description="Date of birth")
    CNIC: str = Field(..., min_length=13, max_length=15, description="National ID number")
    PhoneNo: str = Field(..., min_length=10, max_length=15, description="Phone number required")
    
    # Optional fields with constraints
    UserId: Optional[UUID] = None
    HireDate: Optional[Union[datetime, date]] = None
    Salary: Optional[float] = Field(None, ge=0, description="Salary must be non-negative")
    IsHourlySalary: Optional[bool] = False
    Experience: Optional[int] = Field(None, ge=0, le=50, description="Experience in years (0-50)")
    BloodGroup: Optional[str] = Field(None, max_length=13)
    MobileNo: Optional[str] = Field(None, min_length=10, max_length=15)
    ImagePath: Optional[str] = None
    
    # System fields
    CreatedBy: Optional[UUID] = None
    CreatedDate: Optional[datetime] = None
    IsDeleted: Optional[bool] = False
    IsActive: Optional[bool] = True

    @field_validator('FullName', 'FatherName')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name contains only letters and spaces"""
        if not v or not v.strip():
            raise ValueError('Name cannot be empty or whitespace')
        
        # Allow letters, spaces, hyphens, and apostrophes
        if not re.match(r"^[a-zA-Z\s\-']+$", v):
            raise ValueError('Name can only contain letters, spaces, hyphens, and apostrophes')
        
        # Check for consecutive spaces
        if '  ' in v:
            raise ValueError('Name cannot contain consecutive spaces')
        
        return v.strip()

    @field_validator('Gender')
    @classmethod
    def validate_gender(cls, v: str) -> str:
        """Validate gender is one of accepted values"""
        valid_genders = ['Male', 'Female', 'Other', 'M', 'F']
        if v not in valid_genders:
            raise ValueError(f'Gender must be one of: {", ".join(valid_genders)}')
        
        # Normalize to full name
        if v == 'M':
            return 'Male'
        elif v == 'F':
            return 'Female'
        return v

    @field_validator('DateOfBirth')
    @classmethod
    def validate_date_of_birth(cls, v: Union[datetime, date]) -> datetime:
        """Validate date of birth is reasonable and convert to datetime"""
        # Convert to date if datetime
        if isinstance(v, datetime):
            v_date = v.date()
        else:
            v_date = v
        
        today = date.today()
        age = today.year - v_date.year - ((today.month, today.day) < (v_date.month, v_date.day))
        
        if v_date > today:
            raise HTTPException(status_code=400, detail=f"Date of birth cannot be in the future")
        
        if age < 18:
            raise HTTPException(status_code=400, detail=f"Employee must be at least 18 years old")
        
        if age > 100:
            raise HTTPException(status_code=400, detail=f"Invalid date of birth (age > 100 years)")
        
        # Convert to datetime for database compatibility
        if isinstance(v, date) and not isinstance(v, datetime):
            return datetime.combine(v, datetime.min.time())
        return v

    @field_validator('CNIC')
    @classmethod
    def validate_cnic(cls, v: str) -> str:
        """Validate CNIC format (Pakistan National ID)"""
        # Remove any hyphens or spaces
        cleaned = v.replace('-', '').replace(' ', '')
        
        # Check if it's 13 digits
        if not re.match(r'^\d{13}$', cleaned):
            raise ValueError('CNIC must be 13 digits (format: XXXXX-XXXXXXX-X or XXXXXXXXXXXXX)')
            
        # Return formatted version
        return f"{cleaned[:5]}-{cleaned[5:12]}-{cleaned[12]}"

    @field_validator('PhoneNo', 'MobileNo')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format"""
        if v is None:
            return v
        
        # Remove common separators
        cleaned = v.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
        
        # Check if it contains only digits and optional + at start
        if not re.match(r'^\+?\d{10,15}$', cleaned):
            raise ValueError('Phone number must be 10-15 digits, optionally starting with +')
        
        return cleaned

    @field_validator('BloodGroup')
    @classmethod
    def validate_blood_group(cls, v: Optional[str]) -> Optional[str]:
        """Validate blood group"""
        if v is None:
            return v
        
        valid_blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        v_upper = v.upper().strip()
        
        if v_upper not in valid_blood_groups:
            raise ValueError(f'Blood group must be one of: {", ".join(valid_blood_groups)}')
        
        return v_upper

    @field_validator('Email')
    @classmethod
    def validate_email_domain(cls, v: EmailStr) -> EmailStr:
        """Additional email validation (optional: restrict to company domains)"""
        # Example: Uncomment to restrict to specific domains
        # allowed_domains = ['company.com', 'company.edu']
        # domain = v.split('@')[1]
        # if domain not in allowed_domains:
        #     raise ValueError(f'Email must be from allowed domains: {", ".join(allowed_domains)}')
        
        return v.lower()

    @field_validator('HireDate')
    @classmethod
    def validate_hire_date(cls, v: Optional[Union[datetime, date]]) -> Optional[datetime]:
        """Validate hire date is not in the future and convert to datetime"""
        if v is None:
            return v
        
        # Convert to date if datetime
        if isinstance(v, datetime):
            v_date = v.date()
        else:
            v_date = v
        
        today = date.today()
        if v_date > today:
            raise ValueError('Hire date cannot be in the future')
        
        # Optional: Check if hire date is not too far in the past
        years_ago = today.year - v_date.year
        if years_ago > 50:
            raise ValueError('Hire date cannot be more than 50 years ago')
        
        # Convert to datetime for database compatibility
        if isinstance(v, date) and not isinstance(v, datetime):
            return datetime.combine(v, datetime.min.time())
        return v

    @field_validator('ImagePath')
    @classmethod
    def validate_image_path(cls, v: Optional[str]) -> Optional[str]:
        """Validate image file extension"""
        if v is None:
            return v
        
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        if not any(v.lower().endswith(ext) for ext in allowed_extensions):
            raise ValueError(f'Image must be one of: {", ".join(allowed_extensions)}')
        
        return v

    @model_validator(mode='after')
    def validate_hire_date_vs_dob(self):
        """Cross-field validation: hire date must be after date of birth"""
        if self.HireDate and self.DateOfBirth:
            # Convert to date objects for comparison
            dob_date = self.DateOfBirth.date() if isinstance(self.DateOfBirth, datetime) else self.DateOfBirth
            hire_date = self.HireDate.date() if isinstance(self.HireDate, datetime) else self.HireDate
            
            age_at_hire = hire_date.year - dob_date.year - (
                (hire_date.month, hire_date.day) < (dob_date.month, dob_date.day)
            )
            
            if age_at_hire < 18:
                raise ValueError('Employee must be at least 18 years old at hire date')
        
        return self

    @model_validator(mode='after')
    def validate_salary_requirements(self):
        """Validate salary-related fields"""
        if self.Salary is not None:
            if self.Salary < 0:
                raise ValueError('Salary cannot be negative')
            
            # Optional: Set minimum wage
            MIN_WAGE = 1000  # Adjust based on your requirements
            if self.Salary > 0 and self.Salary < MIN_WAGE:
                raise ValueError(f'Salary must be at least {MIN_WAGE}')
        
        return self

    class Config:
        json_schema_extra = {
            "example": {
                "Email": "john.doe@company.com",
                "CampusId": 1,
                "DesignationId": 5,
                "FullName": "John Doe",
                "FatherName": "Robert Doe",
                "Gender": "Male",
                "DateOfBirth": "1990-05-15",
                "CNIC": "12345-6789012-3",
                "PhoneNo": "+92-300-1234567",
                "MobileNo": "+92-321-9876543",
                "BloodGroup": "O+",
                "HireDate": "2024-01-15",
                "Salary": 50000.00,
                "Experience": 5
            }
        }