from pydantic import BaseModel
from typing import Any, Optional, Generic, TypeVar

T = TypeVar('T')

class StandardResponse(BaseModel, Generic[T]):
    """Standardized API response structure"""
    success: bool
    message: str
    data: Optional[T] = None
    error: Optional[str] = None

    class Config:
        from_attributes = True

def success_response(data: Any = None, message: str = "Operation successful") -> StandardResponse:
    """Create a success response"""
    return StandardResponse(
        success=True,
        message=message,
        data=data,
        error=None
    )

def error_response(message: str, error: str = None) -> StandardResponse:
    """Create an error response"""
    return StandardResponse(
        success=False,
        message=message,
        error=error or message,
        data=None
    )
