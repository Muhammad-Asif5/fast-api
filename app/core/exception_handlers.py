from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.core.response import error_response
from app.schemas.auth_schema import ApiResponse
from fastapi.encoders import jsonable_encoder

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors"""
    errors = []
    for error in exc.errors():
        field = ' -> '.join(str(loc) for loc in error['loc'])
        errors.append({
            "field": field,
            "message": error['msg'],
            "type": error['type']
        })

    raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {errors}"
        )

async def integrity_exception_handler(request: Request, exc: IntegrityError):
    """Handle database integrity errors (duplicates, foreign keys, etc.)"""
    error_message = str(exc.orig)
    
    # Parse common integrity errors
    if 'unique constraint' in error_message.lower():
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "detail": "Duplicate entry",
                "message": "A record with this value already exists"
            }
        )
    elif 'foreign key constraint' in error_message.lower():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": "Invalid reference",
                "message": "Referenced record does not exist"
            }
        )
    elif 'not null constraint' in error_message.lower():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": "Missing required field",
                "message": "A required field is missing"
            }
        )
    
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"Database integrity error: {error_message}",
        errors=[str(exc.orig)]
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle general SQLAlchemy errors"""
    return error_response(
        message="Database error",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        errors=[str(exc)]
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors"""
    return error_response(
        message="Internal server error",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        errors=[str(exc)]
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    response = ApiResponse(
        message="Request failed",
        success=False,
        statusCode=exc.status_code,
        errors=[exc.detail] if isinstance(exc.detail, str) else exc.detail,
        data=None
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(response)
    )

