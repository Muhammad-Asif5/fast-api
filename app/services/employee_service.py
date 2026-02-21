from datetime import date, datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile, status
import os

from app.common.date_utils import ensure_datetime
from app.models.employee_model import Employee
from app.models.user_model import User
from app.repositories.employee_repository import employee_repository
from app.schemas.employee_schema import EmployeeCreate
from app.services.auth_service import AuthService
from app.common import parse_date, validate_image_file, save_uploaded_file

import uuid
from uuid import UUID

class EmployeeService:
    
    def create_employee(self, db: Session, raw_data: dict, current_user: Employee, image: UploadFile | None = None) -> Employee:
        # 1️⃣ Parse, normalize and validate data
        try:
            raw_data["DateOfBirth"] = parse_date(raw_data.get("DateOfBirth"))
            raw_data["HireDate"] = parse_date(raw_data.get("HireDate"))
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid date: {str(e)}")

        gender_map = {"male": "Male", "female": "Female", "other": "Other", "m": "Male", "f": "Female"}
        gender_value = gender_map.get(raw_data.get("Gender", "").lower())
        if not gender_value:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Gender must be one of: Male, Female, Other, M, F"
            )
        raw_data["Gender"] = gender_value

        # 2️⃣ Create Pydantic object (no image yet)
        employee_data = EmployeeCreate(
            **raw_data,
            ImagePath=None,
            CreatedDate=datetime.utcnow(),
            CreatedBy=current_user.EmployeeId if hasattr(current_user, "EmployeeId") else uuid.uuid4(),
            IsDeleted=False,
            Isactive=True
        )

        # 3️⃣ Check duplicates BEFORE saving image
        if employee_repository.get_by_cnic(db, employee_data.CNIC):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Employee with CNIC {employee_data.CNIC} already exists"
            )

        if employee_repository.get_by_email(db, employee_data.Email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Employee with Email {employee_data.Email} already exists"
            )

        # 4️⃣ Now save image safely
        image_path = None
        if image and image.filename:
            try:
                validate_image_file(image)
                image_path = save_uploaded_file(image)
                employee_data.ImagePath = image_path
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Image upload failed: {str(e)}"
                )

        # 5️⃣ Save employee in DB
        try:
            db_employee = employee_repository.create(db, employee_data.dict())
        except Exception as e:
            # If DB save fails, clean up uploaded image
            if image_path and os.path.exists(image_path):
                os.remove(image_path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create employee: {str(e)}"
            )
        return db_employee


    






    
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
                # Handle Date
                # -----------------------
                if "DateOfBirth" in update_fields:
                    update_fields["DateOfBirth"] = ensure_datetime(parse_date(update_fields["DateOfBirth"]))

                if "HireDate" in update_fields:
                    update_fields["HireDate"] = ensure_datetime(parse_date(update_fields["HireDate"]))

                # -----------------------
                # Handle Image
                # -----------------------
                if image and image.filename:
                    validate_image_file(image)
                    image_path = save_uploaded_file(image)
                    update_fields["ImagePath"] = image_path
                    
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

                employee_repository.update(db, employee_id, update_fields)

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