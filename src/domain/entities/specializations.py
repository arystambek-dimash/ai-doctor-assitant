from dataclasses import dataclass


@dataclass(frozen=True)
class SpecializationEntity:
    id: int
    title: str
    description: str


@dataclass(frozen=True)
class SpecializationWithCountEntity:
    id: int
    title: str
    description: str
    doctors_count: int