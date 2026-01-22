from fastapi import HTTPException
from pydantic import BaseModel

class CustomValidationError(HTTPException):
    def __init__(self, code: str, message: str, status_code: int = 400):
        error_response = {
            "error": message,
            "code": code,
        }
        super().__init__(status_code=status_code, detail=error_response)