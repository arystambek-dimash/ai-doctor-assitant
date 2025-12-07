from dataclasses import dataclass


@dataclass
class UserEntity:
    id: int
    email: str
    full_name: str
    password_hash: str
    phone: str
    is_admin: bool


@dataclass
class UserEntityWithDetails:
    id: int
    email: str
    full_name: str
    password_hash: str
    phone: str
    is_admin: bool
    is_doctor: bool
    doctor_id: int
