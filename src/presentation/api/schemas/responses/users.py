from pydantic import BaseModel


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    phone: str
    is_admin: bool
    is_doctor: bool

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str


class MessageResponse(BaseModel):
    message: str
