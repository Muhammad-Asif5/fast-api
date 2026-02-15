from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user_model import User
from app.schemas.auth_schema import UserResponse
from app.repositories.user_repository import user_repository
from app.core.response import success_response

router = APIRouter(prefix="/users", tags=["Users"])


# -------------------------------
# Get all users
# -------------------------------
@router.get("/")
def get_all_users(
    skip: int = 0, 
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all users (Protected endpoint - requires authentication)
    """
    users = user_repository.get_all(db, skip=skip, limit=limit)

    # Convert ORM models to Pydantic schema
    users_schema = [UserResponse.model_validate(user) for user in users]

    # users_schema = [
    #     UserResponse.model_construct(
    #         id=user.id,
    #         username=user.username,
    #         email=user.email,
    #         full_name=user.full_name,
    #         CreatedBy=user.CreatedBy,
    #         Isactive=user.Isactive,
    #         CreatedDate=user.CreatedDate
    #         )
    #         for user in users
    # ]

    return success_response(
        data=users_schema,
        message=f"{len(users_schema)} user(s) retrieved",
        status_code=status.HTTP_200_OK
    )

# -------------------------------
# Get user by ID
# -------------------------------
@router.get("/{user_id}")
def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific user by ID (Protected endpoint - requires authentication)
    """
    user = user_repository.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    user_schema = UserResponse.model_validate(user)
    return success_response(
        data=user_schema,
        message="User retrieved successfully",
        status_code=status.HTTP_200_OK
    )


# -------------------------------
# Delete user
# -------------------------------
@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a user (Protected endpoint - requires authentication)
    
    Note: In a real application, you'd want to add role-based access control
    to ensure only admins can delete users.
    """
    # Prevent users from deleting themselves
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You cannot delete your own account"
        )

    success = user_repository.delete(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    return success_response(
        message=f"User {user_id} deleted successfully",
        status_code=status.HTTP_200_OK
    )


# -------------------------------
# Update profile
# -------------------------------
@router.put("/profile")
def update_profile(
    full_name: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile (Protected endpoint)
    
    Users can only update their own profile.
    """
    update_data = {}
    if full_name is not None:
        update_data["full_name"] = full_name
        
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No update data provided"
        )

    updated_user = user_repository.update(db, current_user.id, update_data)
    updated_user_schema = UserResponse.model_validate(updated_user)

    return success_response(
        data=updated_user_schema,
        message="Profile updated successfully",
        status_code=status.HTTP_200_OK
    )
