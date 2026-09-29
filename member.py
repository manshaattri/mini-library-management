"""Member entity."""
import re
from dataclasses import dataclass, field, asdict
from typing import List

from exceptions import ValidationError

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass
class Member:
    member_id: str
    name: str
    email: str
    borrowed: List[str] = field(default_factory=list)  # book_ids currently held

    def __post_init__(self):
        self.name = (self.name or "").strip()
        self.email = (self.email or "").strip().lower()
        if not self.name:
            raise ValidationError("Member name cannot be empty.")
        if not _EMAIL_RE.match(self.email):
            raise ValidationError(f"Invalid email address: '{self.email}'.")

    def matches(self, query: str) -> bool:
        q = query.strip().lower()
        return q in self.name.lower() or q in self.email or q == self.member_id.lower()

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Member":
        return cls(**data)
