import re
import unicodedata
from dataclasses import dataclass
from typing import Optional

from src.infrastructure.utilities.dto import BaseDTOMixin


def generate_slug(text: str) -> str:
    """Generate a URL-safe slug from text, handling Cyrillic and other Unicode."""
    # Normalize unicode
    text = unicodedata.normalize('NFKD', text)
    # Convert to lowercase
    text = text.lower()
    # Replace spaces and special chars with hyphens
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    # Strip leading/trailing hyphens
    return text.strip('-')


@dataclass
class CreateSpecializationDTO(BaseDTOMixin):
    title: str
    description: str
    slug: Optional[str] = None

    def __post_init__(self):
        if not self.slug:
            self.slug = generate_slug(self.title)


@dataclass
class UpdateSpecializationDTO(BaseDTOMixin):
    title: Optional[str] = None
    description: Optional[str] = None
    slug: Optional[str] = None