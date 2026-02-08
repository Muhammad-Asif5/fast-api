from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class EmployeeResponse(BaseModel):
    CreatedBy: Optional[UUID] = None
    IsActive: bool = Field(alias="Isactive")
    CreatedDate: datetime
    FullName: Optional[str] = None
    FatherName: Optional[str] = None
    Gender: Optional[str] = None
    DateOfBirth: Optional[datetime] = None
    CNIC: Optional[str] = None
    BloodGroup: Optional[str] = None
    MobileNo: Optional[str] = None
    PhoneNo: Optional[str] = None
    ImagePath: Optional[str] = None
    

    class Config:
        from_attributes = True
        populate_by_name = True

class EmployeeCreate(BaseModel):
    email: EmailStr
    CampusId: Optional[int] = None
    UserId: Optional[UUID] = None
    DesignationId: Optional[int] = None
    HireDate: Optional[datetime] = None
    Salary: Optional[float] = None
    IsHourlySalary: Optional[bool] = None
    Experience: Optional[int] = None
    FullName: Optional[str] = None
    FatherName: Optional[str] = None
    Gender: Optional[str] = None
    DateOfBirth: Optional[datetime] = None
    CNIC: Optional[str] = None
    BloodGroup: Optional[str] = None
    MobileNo: Optional[str] = None
    PhoneNo: Optional[str] = None
    ImagePath: Optional[str] = None
    CreatedBy: Optional[UUID] = None
    CreatedDate: Optional[datetime] = None
    IsDeleted: Optional[bool] = False
    Isactive: Optional[bool] = True

