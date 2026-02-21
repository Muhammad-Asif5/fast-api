from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.core.response import error_response
from app.schemas.auth_schema import ApiResponse
from fastapi.encoders import jsonable_encoder

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = [
        f"{' -> '.join(str(loc) for loc in e['loc'])}: {e['msg']}"
        for e in exc.errors()
    ]
    return error_response(
        message="Validation failed",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        errors=errors,
    )


async def integrity_exception_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    msg = str(exc.orig).lower()
    if "unique" in msg:
        return error_response("A record with this value already exists", status.HTTP_409_CONFLICT)
    if "foreign key" in msg:
        return error_response("Referenced record does not exist", status.HTTP_400_BAD_REQUEST)
    if "not null" in msg:
        return error_response("A required field is missing", status.HTTP_400_BAD_REQUEST)
    return error_response(f"Database integrity error", status.HTTP_409_CONFLICT, errors=[str(exc.orig)])


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    return error_response("Database error", status.HTTP_500_INTERNAL_SERVER_ERROR, errors=[str(exc)])


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, errors=[str(exc)])


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    errors = [exc.detail] if isinstance(exc.detail, str) else exc.detail
    payload = ApiResponse(
        message="Request failed",
        success=False,
        statusCode=exc.status_code,
        errors=errors,
        data=None,
    )
    return JSONResponse(status_code=exc.status_code, content=jsonable_encoder(payload))