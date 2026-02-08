from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.employee_model import Employee
from app.models.user_model import User
from app.repositories.employee_repository import employee_repository
from app.schemas.employee_schema import EmployeeCreate
from app.services.auth_service import AuthService

class EmployeeService:
    
    @staticmethod
    def register_user(db: Session, user_data: EmployeeCreate) -> Employee:
        """Register a new user"""
        # # Check if username already exists
        # existing_user = employee_repository.get_by_username(db, user_data.username)
        # if existing_user:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail=f"Username ({user_data.username}) already registered"
        #     )
        
        # # Check if email already exists
        # existing_email = employee_repository.get_by_email(db, user_data.email)
        # if existing_email:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail=f"Email ({user_data.email}) already registered"
        #     )
        
        # # Hash the password
        # hashed_password = AuthService.get_password_hash(user_data.password)
        # user_data.hashed_password = hashed_password
        # Create the user
        new_user = employee_repository.create_employee(db, user_data)
        return new_user
    

employee_service = EmployeeService()