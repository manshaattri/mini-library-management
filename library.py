"""Core business logic: Books, Members, Issue/Return."""
import logging
from datetime import date, timedelta
from typing import Dict, List, Optional

from book import Book
from member import Member
from exceptions import (BookNotAvailableError, BookNotFoundError, DuplicateError,
                        IssueLimitError, MemberNotFoundError, NotIssuedError)

log = logging.getLogger(__name__)


class Library:
    MAX_BOOKS_PER_MEMBER = 3
    LOAN_DAYS = 14
    FINE_PER_DAY = 2  # currency units per overdue day

    def __init__(self, storage=None):
        self.storage = storage
        self.books: Dict[str, Book] = {}
        self.members: Dict[str, Member] = {}
        if storage:
            data = storage.load()
            self.books = {b["book_id"]: Book.from_dict(b) for b in data.get("books", [])}
            self.members = {m["member_id"]: Member.from_dict(m) for m in data.get("members", [])}

    # ---------- helpers ----------
    def _save(self) -> None:
        if self.storage:
            self.storage.save({"books": [b.to_dict() for b in self.books.values()],
                               "members": [m.to_dict() for m in self.members.values()]})

    @staticmethod
    def _next_id(prefix: str, existing) -> str:
        nums = [int(i[len(prefix):]) for i in existing if i[len(prefix):].isdigit()]
        return f"{prefix}{(max(nums) + 1 if nums else 1):03d}"

    def get_book(self, book_id: str) -> Book:
        try:
            return self.books[book_id.strip().upper()]
        except KeyError:
            raise BookNotFoundError(f"No book with ID '{book_id}'.") from None

    def get_member(self, member_id: str) -> Member:
        try:
            return self.members[member_id.strip().upper()]
        except KeyError:
            raise MemberNotFoundError(f"No member with ID '{member_id}'.") from None

    # ---------- Module 1: Book management ----------
    def add_book(self, title: str, author: str) -> Book:
        book = Book(self._next_id("B", self.books), title, author)  # validates
        if any(b.title.lower() == book.title.lower() and b.author.lower() == book.author.lower()
               for b in self.books.values()):
            raise DuplicateError(f"'{book.title}' by {book.author} already exists.")
        self.books[book.book_id] = book
        self._save()
        log.info("Book added: %s '%s'", book.book_id, book.title)
        return book

    def view_books(self) -> List[Book]:
        return sorted(self.books.values(), key=lambda b: b.book_id)

    def search_books(self, query: str) -> List[Book]:
        return [b for b in self.view_books() if b.matches(query)]

    def remove_book(self, book_id: str) -> Book:
        book = self.get_book(book_id)
        if not book.is_available:
            raise BookNotAvailableError(f"'{book.title}' is currently issued and cannot be removed.")
        del self.books[book.book_id]
        self._save()
        log.info("Book removed: %s", book.book_id)
        return book

    # ---------- Module 2: Member management ----------
    def add_member(self, name: str, email: str) -> Member:
        member = Member(self._next_id("M", self.members), name, email)  # validates
        if any(m.email == member.email for m in self.members.values()):
            raise DuplicateError(f"A member with email '{member.email}' already exists.")
        self.members[member.member_id] = member
        self._save()
        log.info("Member added: %s '%s'", member.member_id, member.name)
        return member

    def view_members(self) -> List[Member]:
        return sorted(self.members.values(), key=lambda m: m.member_id)

    def search_members(self, query: str) -> List[Member]:
        return [m for m in self.view_members() if m.matches(query)]

    # ---------- Module 3: Issue & return ----------
    def check_availability(self, book_id: str) -> bool:
        return self.get_book(book_id).is_available

    def issue_book(self, book_id: str, member_id: str, today: Optional[date] = None) -> Book:
        today = today or date.today()
        book, member = self.get_book(book_id), self.get_member(member_id)
        if not book.is_available:
            raise BookNotAvailableError(f"'{book.title}' is already issued to {book.issued_to}.")
        if len(member.borrowed) >= self.MAX_BOOKS_PER_MEMBER:
            raise IssueLimitError(f"{member.name} already has {self.MAX_BOOKS_PER_MEMBER} books.")
        book.issued_to = member.member_id
        book.due_date = (today + timedelta(days=self.LOAN_DAYS)).isoformat()
        member.borrowed.append(book.book_id)
        self._save()
        log.info("Issued %s to %s (due %s)", book.book_id, member.member_id, book.due_date)
        return book

    def return_book(self, book_id: str, today: Optional[date] = None) -> int:
        """Returns the fine (0 if on time)."""
        today = today or date.today()
        book = self.get_book(book_id)
        if book.is_available:
            raise NotIssuedError(f"'{book.title}' is not currently issued.")
        fine = self.calculate_fine(book, today)
        member = self.members.get(book.issued_to)
        if member and book.book_id in member.borrowed:
            member.borrowed.remove(book.book_id)
        book.issued_to = book.due_date = None
        self._save()
        log.info("Returned %s (fine=%s)", book.book_id, fine)
        return fine

    def calculate_fine(self, book: Book, today: Optional[date] = None) -> int:
        if not book.due_date:
            return 0
        overdue = ((today or date.today()) - date.fromisoformat(book.due_date)).days
        return max(0, overdue) * self.FINE_PER_DAY
