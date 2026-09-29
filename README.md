# Mini Library Management System

A modular, menu-driven Python application to manage a small library's books, members, and book circulation.

## Overview
Built for the VITyarthi *Build Your Own Project* evaluation. It demonstrates object-oriented design, separation of concerns (entities / business logic / storage / UI), input validation, custom exception handling, logging, JSON persistence and unit testing.

## Features
- **Book Management** - add, view all, search (title/author/ID), remove (blocked if issued)
- **Member Management** - add (email validated, unique), view, search
- **Issue & Return** - 14-day loans, max 3 books per member, late fine of 2/day, availability check
- **Reports** - available books, issued books (with OVERDUE status), library summary
- Auto-generated IDs (`B001`, `M001`), atomic JSON saves, activity log in `library.log`

## Technologies
Python 3.8+ (standard library only): `dataclasses`, `json`, `logging`, `unittest`. Git for version control.

## Project Structure
```
main.py        CLI menus           library.py   business logic
book.py        Book entity         reports.py   report generation
member.py      Member entity       storage.py   JSON persistence
exceptions.py  custom errors       tests/       unit tests
docs/design.md UML + flow diagrams data/        library.json (auto-created)
```

## Install & Run
```bash
git clone <your-repo-url>
cd mini-library-management
python main.py          # no pip install needed
```

## Testing
```bash
python -m unittest discover -s tests -v
```

