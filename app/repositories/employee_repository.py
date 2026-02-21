from typing import Optional
from sqlalchemy.orm import Session
from app.models.employee_model import Employee
from app.repositories.base import BaseRepository


class EmployeeRepository(BaseRepository[Employee]):
    def __init__(self):
        super().__init__(Employee)

    # ---------------------------------------------------------
    # Employee Specific Queries Only
    # ---------------------------------------------------------
    def get_by_email(self, db: Session, email: str) -> Optional[Employee]:
        return self._base_query(db).filter(Employee.Email == email).first()

    def get_by_cnic(self, db: Session, cnic: str) -> Optional[Employee]:
        return self._base_query(db).filter(Employee.CNIC == cnic).first()


    def exists_by_email(self, db: Session, email: str, exclude_id: Optional[int] = None) -> bool:
            q = self._base_query(db).filter(Employee.Email == email)
            if exclude_id is not None:
                q = q.filter(Employee.EmployeeId != exclude_id)
            return q.first() is not None

    def exists_by_cnic(self, db: Session, cnic: str, exclude_id: Optional[int] = None) -> bool:
        q = self._base_query(db).filter(Employee.CNIC == cnic)
        if exclude_id is not None:
            q = q.filter(Employee.EmployeeId != exclude_id)
        return q.first() is not None

# Singleton
employee_repository = EmployeeRepository()
