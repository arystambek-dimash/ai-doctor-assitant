from typing import Optional

from pydantic import BaseModel, Field


class SpecializationCreateRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=100)
    description: str = Field(..., min_length=10, max_length=1000)

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Cardiology",
                "description": "Branch of medicine dealing with disorders of the heart and cardiovascular system."
            }
        }


class SpecializationUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, min_length=10, max_length=1000)
