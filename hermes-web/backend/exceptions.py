"""
Custom exceptions for ZSCE Agent Web Application
"""

from fastapi import HTTPException, status
from typing import Any, Dict, Optional

class ZSCEException(Exception):
    """Base exception for ZSCE Agent application"""
    def __init__(self, message: str, code: str = None, details: Any = None):
        self.message = message
        self.code = code
        self.details = details
        super().__init__(self.message)

class AuthenticationError(ZSCEException):
    """Authentication related errors"""
    def __init__(self, message: str = "Authentication failed", details: Any = None):
        super().__init__(message, "AUTH_ERROR", details)

class AuthorizationError(ZSCEException):
    """Authorization related errors"""
    def __init__(self, message: str = "Access denied", details: Any = None):
        super().__init__(message, "AUTHZ_ERROR", details)

class ValidationError(ZSCEException):
    """Data validation errors"""
    def __init__(self, message: str = "Validation failed", details: Any = None):
        super().__init__(message, "VALIDATION_ERROR", details)

class ResourceNotFoundError(ZSCEException):
    """Resource not found errors"""
    def __init__(self, resource: str, resource_id: Any, details: Any = None):
        message = f"{resource} with id {resource_id} not found"
        super().__init__(message, "NOT_FOUND", details)

class WorkflowError(ZSCEException):
    """Workflow related errors"""
    def __init__(self, message: str = "Workflow operation failed", details: Any = None):
        super().__init__(message, "WORKFLOW_ERROR", details)

class ExternalServiceError(ZSCEException):
    """External service integration errors"""
    def __init__(self, service: str, message: str = "External service error", details: Any = None):
        message = f"{service}: {message}"
        super().__init__(message, "EXTERNAL_SERVICE_ERROR", details)

def handle_zsce_exception(exc: ZSCEException) -> HTTPException:
    """Convert ZSCE exceptions to HTTP exceptions"""
    status_code_map = {
        "AUTH_ERROR": status.HTTP_401_UNAUTHORIZED,
        "AUTHZ_ERROR": status.HTTP_403_FORBIDDEN,
        "VALIDATION_ERROR": status.HTTP_400_BAD_REQUEST,
        "NOT_FOUND": status.HTTP_404_NOT_FOUND,
        "WORKFLOW_ERROR": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "EXTERNAL_SERVICE_ERROR": status.HTTP_502_BAD_GATEWAY,
    }
    
    status_code = status_code_map.get(exc.code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return HTTPException(
        status_code=status_code,
        detail={
            "error": exc.message,
            "code": exc.code,
            "details": exc.details
        }
    )
