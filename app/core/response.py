from typing import TypeVar, Optional, List
from fastapi.responses import JSONResponse
from fastapi import status
from fastapi.encoders import jsonable_encoder

from app.schemas.auth_schema import ApiResponse

T = TypeVar("T")


def success_response(
    data: Optional[T] = None,
    message: str = "Success",
    status_code: int = status.HTTP_200_OK,
):
    response = ApiResponse(
        message=message,
        success=True,
        statusCode=status_code,
        errors=[],
        data=data,
    )

    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(response)  # ✅ FIX HERE
    )


def error_response(
    message: str = "Error",
    status_code: int = status.HTTP_400_BAD_REQUEST,
    errors: Optional[List[str]] = None,
):
    response = ApiResponse(
        message=message,
        success=False,
        statusCode=status_code,
        errors=errors or [],
        data=None,
    )

    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(response)  # ✅ FIX HERE
    )
