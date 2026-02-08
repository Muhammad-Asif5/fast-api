from typing import Optional
from sqlalchemy.orm import Session
from app.models.employee_model import Employee
from app.repositories.base import BaseRepository
from app.schemas.employee_schema import EmployeeCreate


class EmployeeRepository(BaseRepository[Employee]):
    def __init__(self):
        super().__init__(Employee)

    def create_employee(self, db: Session, employee_data: EmployeeCreate) -> Employee:
        # Convert Pydantic schema to SQLAlchemy model
        db_employee = Employee(
            CampusId=int(employee_data.CampusId) if employee_data.CampusId else None,
            UserId=employee_data.UserId,
            DesignationId=int(employee_data.DesignationId) if employee_data.DesignationId else None,
            HireDate=employee_data.HireDate,
            Salary=float(employee_data.Salary) if employee_data.Salary else None,
            IsHourlySalary=bool(employee_data.IsHourlySalary) if employee_data.IsHourlySalary else False,
            Experience=int(employee_data.Experience) if employee_data.Experience else None,
            FullName=employee_data.FullName,
            FatherName=employee_data.FatherName,
            Gender=employee_data.Gender,
            DateOfBirth=employee_data.DateOfBirth,
            CNIC=employee_data.CNIC,
            BloodGroup=employee_data.BloodGroup,
            MobileNo=employee_data.MobileNo,
            PhoneNo=employee_data.PhoneNo,
            Email=employee_data.email,
            ImagePath=employee_data.ImagePath,
            CreatedBy=employee_data.CreatedBy,
            CreatedDate=employee_data.CreatedDate,
            IsDeleted=employee_data.IsDeleted,
            Isactive=employee_data.Isactive
        )
        
        db.add(db_employee)
        db.commit()
        db.refresh(db_employee)
        return db_employee

    def get_all(self, db: Session, skip=0, limit=100):
        return super().get_all(db, skip, limit, order_by="EmployeeId")
    
employee_repository = EmployeeRepository()