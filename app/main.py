from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine
from app.api.v1 import users
from app.api.v1 import auth_controller, employee_controller
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.core.exception_handlers import (
    http_exception_handler,
    validation_exception_handler,
    integrity_exception_handler,
    sqlalchemy_exception_handler,
    general_exception_handler
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG,
    description="""
    LMS (Learning Management System) API with comprehensive employee management.
    
    ## Features
    
    * **JWT Authentication** - Secure token-based authentication
    * **Employee Management** - CRUD operations with validation
    * **File Upload** - Profile image handling
    * **Data Validation** - Comprehensive input validation
    
    ## Authentication
    
    Most endpoints require JWT authentication. Include the token in the Authorization header:
    ```
    Authorization: Bearer <your_token>
    ```
    """
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(IntegrityError, integrity_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

# Include routers
app.include_router(auth_controller.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(employee_controller.router, prefix="/api/v1")


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Welcome to LMS FastAPI with JWT Authentication",
        "version": settings.VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "authentication": "JWT Bearer Token",
        "features": [
            "Employee Management",
            "User Authentication",
            "File Upload",
            "Comprehensive Validation"
        ]
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        # You can add database connectivity check here
        return {
            "status": "healthy",
            "version": settings.VERSION,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    from datetime import datetime
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")

    