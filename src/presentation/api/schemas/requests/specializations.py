from pydantic import BaseModel


class SpecializationResponse(BaseModel):
    id: int
    title: str
    description: str

    class Config:
        from_attributes = True


class SpecializationWithCountResponse(BaseModel):
    id: int
    title: str
    description: str
    doctors_count: int

    class Config:
        from_attributes = True
