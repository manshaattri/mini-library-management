"""Module 4: Reports (pure read-only functions over a Library)."""
from datetime import date
from typing import List, Optional, Sequence

from library import Library


def format_table(headers: Sequence[str], rows: List[Sequence]) -> str:
    """Render rows as an aligned text table."""
    if not rows:
        return "  (nothing to show)"
    rows = [[str(c) for c in r] for r in rows]
    widths = [max(len(h), *(len(r[i]) for r in rows)) for i, h in enumerate(headers)]
    line = "-+-".join("-" * w for w in widths)
    fmt = " | ".join(f"{{:<{w}}}" for w in widths)
    return "\n".join([fmt.format(*headers), line] + [fmt.format(*r) for r in rows])


def available_books_report(lib: Library) -> str:
    rows = [(b.book_id, b.title, b.author) for b in lib.view_books() if b.is_available]
    return format_table(["ID", "Title", "Author"], rows)


def issued_books_report(lib: Library, today: Optional[date] = None) -> str:
    today = today or date.today()
    rows = []
    for b in lib.view_books():
        if not b.is_available:
            m = lib.members.get(b.issued_to)
            status = "OVERDUE" if date.fromisoformat(b.due_date) < today else "On time"
            rows.append((b.book_id, b.title, m.name if m else b.issued_to, b.due_date, status))
    return format_table(["ID", "Title", "Issued To", "Due", "Status"], rows)


def summary_data(lib: Library, today: Optional[date] = None) -> dict:
    today = today or date.today()
    issued = [b for b in lib.books.values() if not b.is_available]
    return {
        "total_books": len(lib.books),
        "available": len(lib.books) - len(issued),
        "issued": len(issued),
        "members": len(lib.members),
        "overdue": sum(date.fromisoformat(b.due_date) < today for b in issued),
    }


def summary_report(lib: Library, today: Optional[date] = None) -> str:
    s = summary_data(lib, today)
    return (f"  Total books   : {s['total_books']}\n  Available     : {s['available']}\n"
            f"  Issued        : {s['issued']}\n  Overdue       : {s['overdue']}\n"
            f"  Total members : {s['members']}")
