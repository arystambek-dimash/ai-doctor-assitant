from dataclasses import dataclass


@dataclass(frozen=True)
class UserEntity:
    id: int
    email: str
    full_name: str
    password_hash: str
    phone: str
    is_admin: bool
