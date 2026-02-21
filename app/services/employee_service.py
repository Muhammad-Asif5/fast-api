from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import os

from app.models.employee_model import Employee
from app.models.user_model import User
from app.repositories.employee_repository import employee_repository
from app.schemas.employee_schema import EmployeeCreate
from app.services.auth_service import AuthService
from app.common import parse_date, validate_image_file, save_uploaded_file

import uuid
from uuid import UUID

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
    
    def create_employee(
        self,
        db: Session,
        employee_data: EmployeeCreate,
        image=None,
        current_user: Employee = None
    ) -> Employee:

        image_path = None

        try:
            # -----------------------
            # Handle Image
            # -----------------------
            if image and image.filename:
                validate_image_file(image)
                image_path = save_uploaded_file(image)
                employee_data.ImagePath = image_path

            # -----------------------
            # Parse Dates
            # -----------------------
            if employee_data.DateOfBirth:
                employee_data.DateOfBirth = parse_date(employee_data.DateOfBirth)
            if employee_data.HireDate:
                employee_data.HireDate = parse_date(employee_data.HireDate)

            # -----------------------
            # Set audit fields
            # -----------------------
            employee_data.CreatedDate = datetime.utcnow()
            employee_data.CreatedBy = (
                getattr(current_user, "EmployeeId", uuid.uuid4())
            )
            employee_data.IsDeleted = False
            employee_data.Isactive = True

            # -----------------------
            # Duplicate Checks
            # -----------------------
            if employee_repository.get_by_id(db, employee_data.UserId):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"UserId ({employee_data.UserId}) already exists"
                )

            if db.query(Employee).filter(
                Employee.CNIC == employee_data.CNIC,
                Employee.IsDeleted == False
            ).first():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Employee with this CNIC already exists"
                )

            if employee_repository.get_by_email(db, employee_data.email):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Employee with this email already exists"
                )

            # -----------------------
            # Create Employee
            # -----------------------
            new_employee = employee_repository.create_employee(db, employee_data)
            return new_employee

        except HTTPException:
            # Clean up uploaded image on any known error
            if image_path and os.path.exists(image_path):
                os.remove(image_path)
            raise

        except Exception as e:
            if image_path and os.path.exists(image_path):
                os.remove(image_path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create employee: {str(e)}"
            )
    
    def update_employee(self,db: Session, employee_id: int, update_fields: dict, image, current_user: Employee):

            employee = employee_repository.get_by_id(db, employee_id)

            if not employee or employee.IsDeleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Employee with ID {employee_id} not found"
                )

            old_image_path = employee.ImagePath
            image_path = old_image_path

            try:
                # -----------------------
                # Handle Image
                # -----------------------
                if image and image.filename:
                    validate_image_file(image)
                    image_path = save_uploaded_file(image)
                    update_fields["ImagePath"] = image_path
                    
                # -----------------------
                # Handle Date
                # -----------------------
                if "DateOfBirth" in update_fields:
                    update_fields["DateOfBirth"] = parse_date(
                        update_fields["DateOfBirth"]
                    )

                # Remove None values
                update_fields = {
                    k: v for k, v in update_fields.items()
                    if v is not None
                }

                # Apply dynamic update
                for key, value in update_fields.items():
                    setattr(employee, key, value)

                # Audit fields
                employee.UpdatedDate = datetime.utcnow()
                employee.UpdatedBy = getattr(current_user, "EmployeeId", None)

                db.commit()
                db.refresh(employee)

                # Delete old image
                if image and image.filename and old_image_path and os.path.exists(old_image_path):
                    os.remove(old_image_path)

                return employee

            except Exception as e:
                db.rollback()

                if image_path != old_image_path and os.path.exists(image_path):
                    os.remove(image_path)

                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to update employee: {str(e)}"
                )

employee_service = EmployeeService()