import traceback
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from services.exceptions import AppException
from services.logging_service import get_logger

logger = get_logger(__name__)

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except AppException as e:
            # Handle our custom app exceptions
            logger.warning(f"AppException: {e.message} (Code: {e.error_code})")
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "error": e.message,
                    "code": e.error_code,
                    "details": e.details
                }
            )
        except Exception as e:
            # Handle unhandled system exceptions
            error_id = traceback.format_exc()
            logger.error(f"Unhandled Exception: {str(e)}\n{error_id}")
            
            # Sanitized response for client
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "code": "INTERNAL_SERVER_ERROR",
                    "detail": "An unexpected error occurred. Please contact support."
                }
            )
