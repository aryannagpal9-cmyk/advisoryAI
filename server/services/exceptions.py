from typing import Any, Optional

class AppException(Exception):
    def __init__(
        self, 
        message: str, 
        status_code: int = 500, 
        error_code: Optional[str] = None,
        details: Any = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details

class DatabaseError(AppException):
    def __init__(self, message: str, details: Any = None):
        super().__init__(
            message=message, 
            status_code=500, 
            error_code="DATABASE_ERROR", 
            details=details
        )

class NotFoundError(AppException):
    def __init__(self, message: str):
        super().__init__(
            message=message, 
            status_code=404, 
            error_code="NOT_FOUND"
        )

class ValidationError(AppException):
    def __init__(self, message: str, details: Any = None):
        super().__init__(
            message=message, 
            status_code=400, 
            error_code="VALIDATION_ERROR", 
            details=details
        )

class AuthError(AppException):
    def __init__(self, message: str):
        super().__init__(
            message=message, 
            status_code=401, 
            error_code="AUTH_ERROR"
        )
