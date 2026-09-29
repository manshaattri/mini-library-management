# Problem Statement

## Problem
Small libraries (college departments, clubs, community reading rooms) often track books and borrowers in paper registers or spreadsheets. This causes duplicate entries, lost track of who holds which book, missed due dates, and no quick view of library status.

## Scope
A menu-driven, offline Python application that manages books, members, book issue/return (with due dates and late fines) and basic reports. Data is stored locally in a JSON file.
Out of scope: web/GUI front-end, multi-user login, online payments, barcode scanning.

## Target Users
- Librarians / library assistants (primary)
- Student volunteers running small departmental libraries

## High-Level Features
1. **Book Management** - add, view, search, remove books
2. **Member Management** - add, view, search members
3. **Issue & Return** - issue, return (auto late-fine), check availability
4. **Reports** - available books, issued books (with overdue flag), library summary
