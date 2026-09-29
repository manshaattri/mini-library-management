"""Book entity."""
from dataclasses import dataclass, asdict
from typing import Optional

from exceptions import ValidationError


@dataclass
class Book:
    book_id: str
    title: str
    author: str
    issued_to: Optional[str] = None   # member_id, or None if on the shelf
    due_date: Optional[str] = None    # ISO date string, or None

    def __post_init__(self):
        self.title = (self.title or "").strip()
        self.author = (self.author or "").strip()
        if not self.title:
            raise ValidationError("Book title cannot be empty.")
        if not self.author:
            raise ValidationError("Book author cannot be empty.")

    @property
    def is_available(self) -> bool:
        return self.issued_to is None

    def matches(self, query: str) -> bool:
        q = query.strip().lower()
        return q in self.title.lower() or q in self.author.lower() or q == self.book_id.lower()

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Book":
        return cls(**data)
