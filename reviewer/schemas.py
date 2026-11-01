from typing import Literal
from pydantic import BaseModel

class Finding(BaseModel):
    file: str
    line: int
    type: Literal["security", "error_handling", "missing_test", "bug", "other"]
    severity: Literal["low", "medium", "high"]
    message: str
    suggestion: str

class Review(BaseModel):
    findings: list[Finding]