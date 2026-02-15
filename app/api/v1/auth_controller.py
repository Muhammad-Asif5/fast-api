from email import message
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth_schema import ApiResponse, UserCreate, UserLogin, UserResponse, Token
from app.services.auth_service import auth_service
from app.core.response import success_response

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    
    - **username**: unique username (3-50 characters)
    - **email**: valid email address
    - **password**: password (minimum 6 characters)
    - **full_name**: optional full name
    """
    new_user = auth_service.register_user(db, user_data)
    if not new_user:
        raise HTTPException(status_code=400, detail="User registration failed")
    # user_schema = UserResponse.model_validate(new_user)
    return success_response(new_user, "User created", 201)

@router.post("/login", response_model=ApiResponse[Token])
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login with username and password
    
    - **username**: your username
    - **password**: your password
    
    Returns a JWT access token
    """
    token = auth_service.login(db, login_data.username, login_data.password)
    user = auth_service.authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password 111",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return success_response(
        data=token,
        message="Login successful",
        status_code=200
    )
