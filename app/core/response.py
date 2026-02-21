from typing import TypeVar, Optional, List, Any
from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from app.schemas.auth_schema import ApiResponse

T = TypeVar("T")

def _build_response(
    *,
    success: bool,
    message: str,
    status_code: int,
    data: Optional[Any] = None,
    errors: Optional[List[str]] = None,
) -> JSONResponse:
    payload = ApiResponse(
        message=message,
        success=success,
        statusCode=status_code,
        errors=errors or [],
        data=data,
    )
    return JSONResponse(status_code=status_code, content=jsonable_encoder(payload))

def success_response(
    data: Optional[T] = None,
    message: str = "Success",
    status_code: int = status.HTTP_200_OK,
) -> JSONResponse:
    return _build_response(success=True, message=message, status_code=status_code, data=data)

def error_response(
    message: str = "Error",
    status_code: int = status.HTTP_400_BAD_REQUEST,
    errors: Optional[List[str]] = None,
) -> JSONResponse:
    return _build_response(success=False, message=message, status_code=status_code, errors=errors)
