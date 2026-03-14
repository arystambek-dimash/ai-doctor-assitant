from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SpecializationEntity:
    id: int
    title: str
    slug: str
    description: Optional[str]


@dataclass(frozen=True)
class SpecializationWithCountEntity:
    id: int
    title: str
    slug: str
    description: Optional[str]
    doctors_count: int