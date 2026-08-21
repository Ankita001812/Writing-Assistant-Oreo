from pydantic import BaseModel, field_validator
from typing import Literal

# Allow-list of supported modes — matches the writing-modes spec.
Mode = Literal["grammar", "paraphrase", "formal", "polite", "friendly", "concise"]

class ImproveRequest(BaseModel):
    text: str
    mode: Mode = "grammar"   # defaults to grammar-correction if not sent

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("text must not be empty or whitespace-only")
        if len(v) > 2000:
            raise ValueError("text is too long (max 2000 characters)")
        return v

class ImproveResponse(BaseModel):
    original_text: str
    mode: str
    improved_text: str

class HealthResponse(BaseModel):
    status: str