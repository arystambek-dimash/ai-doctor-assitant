from dataclasses import dataclass


@dataclass(frozen=True)
class UserEntity:
    id: int
    email: str
    password_hash: str
    full_name: str
    phone: str
    is_admin: bool


