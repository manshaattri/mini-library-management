"""Custom exceptions so callers can handle each failure case explicitly."""


class LibraryError(Exception):
    """Base class for every error raised by the library system."""


class ValidationError(LibraryError):
    """Input failed validation (empty title, bad email, ...)."""


class DuplicateError(LibraryError):
    """Entity already exists."""


class BookNotFoundError(LibraryError):
    """No book with the given ID."""


class MemberNotFoundError(LibraryError):
    """No member with the given ID."""


class BookNotAvailableError(LibraryError):
    """Book is already issued / cannot be removed or issued."""


class IssueLimitError(LibraryError):
    """Member reached the maximum number of borrowed books."""


class NotIssuedError(LibraryError):
    """Book being returned is not currently issued."""


class StorageError(LibraryError):
    """Data file could not be read or written."""
