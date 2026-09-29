# Design Document

## 1. Functional Requirements
| Module | Requirements |
|---|---|
| Book Management | FR1 add book, FR2 view all, FR3 search, FR4 remove |
| Member Management | FR5 add member, FR6 view members, FR7 search member |
| Issue & Return | FR8 issue, FR9 return (+fine), FR10 check availability |
| Reports | FR11 available books, FR12 issued books, FR13 summary |

## 2. Non-Functional Requirements
1. **Reliability** - atomic file writes; corrupt data file reported cleanly, never overwritten silently.
2. **Usability** - numbered menus, clear error messages, case-insensitive IDs and search.
3. **Maintainability** - layered modules, one responsibility each, type hints, docstrings.
4. **Error handling** - custom exception hierarchy; unexpected errors caught and logged, app stays alive.
5. **Logging** - every state change written to `library.log`.
6. **Testability** - business logic has no I/O; date is injectable; 16 unit tests.

## 3. System Architecture
```mermaid
flowchart TB
    U[Librarian] --> UI[main.py - CLI menus]
    UI --> L[library.py - business logic]
    UI --> R[reports.py - reports]
    R --> L
    L --> E[book.py / member.py - entities]
    L --> S[storage.py - JSON persistence]
    S --> D[(data/library.json)]
    L -.-> LOG[(library.log)]
    L -.-> X[exceptions.py]
```

## 4. Workflow: Issue a Book
```mermaid
flowchart TD
    A([Start]) --> B[Enter Book ID and Member ID]
    B --> C{Book exists?}
    C -- No --> Z1[Error: BookNotFound] --> Q([End])
    C -- Yes --> D{Member exists?}
    D -- No --> Z2[Error: MemberNotFound] --> Q
    D -- Yes --> E{Book available?}
    E -- No --> Z3[Error: BookNotAvailable] --> Q
    E -- Yes --> F{Member under limit?}
    F -- No --> Z4[Error: IssueLimit] --> Q
    F -- Yes --> G[Set issued_to, due_date = today + 14d]
    G --> H[Save to JSON and log] --> I[Show due date] --> Q
```

## 5. Use Case Diagram
```mermaid
flowchart LR
    Lib((Librarian))
    subgraph System
      UC1[Manage Books]
      UC2[Manage Members]
      UC3[Issue Book]
      UC4[Return Book]
      UC5[Check Availability]
      UC6[View Reports]
    end
    Lib --- UC1 & UC2 & UC3 & UC4 & UC5 & UC6
    UC4 -. include .-> UC7[Calculate Fine]
```

## 6. Class Diagram
```mermaid
classDiagram
    class Book { +book_id +title +author +issued_to +due_date +is_available() +matches(q) }
    class Member { +member_id +name +email +borrowed[] +matches(q) }
    class Library {
      +books +members
      +add_book() +remove_book() +search_books()
      +add_member() +search_members()
      +issue_book() +return_book() +check_availability()
      +calculate_fine()
    }
    class JsonStorage { +load() +save() }
    class Reports { +available_books_report() +issued_books_report() +summary_report() }
    class LibraryError
    Library "1" o-- "*" Book
    Library "1" o-- "*" Member
    Library --> JsonStorage
    Reports ..> Library
    LibraryError <|-- ValidationError
    LibraryError <|-- BookNotAvailableError
    LibraryError <|-- IssueLimitError
```

## 7. Sequence Diagram: Return a Book
```mermaid
sequenceDiagram
    actor L as Librarian
    participant UI as main.py
    participant Lib as Library
    participant St as JsonStorage
    L->>UI: Return book B001
    UI->>Lib: return_book("B001")
    Lib->>Lib: get_book, check issued
    Lib->>Lib: calculate_fine(due_date, today)
    Lib->>Lib: clear issued_to, update member
    Lib->>St: save(data)
    St-->>Lib: ok
    Lib-->>UI: fine
    UI-->>L: "Returned. Late fine: N"
```

## 8. Storage Design (JSON schema)
```mermaid
erDiagram
    MEMBER ||--o{ BOOK : borrows
    MEMBER { string member_id PK  string name  string email  list borrowed }
    BOOK { string book_id PK  string title  string author  string issued_to FK  string due_date }
```

## 9. Design Decisions & Rationale
- **Layered structure** keeps UI, logic and storage independently testable/replaceable.
- **JSON storage** - zero dependencies, human-readable; `JsonStorage` can be swapped for SQLite.
- **Custom exceptions** let the UI show precise messages without parsing strings.
- **Injectable `today`** makes date-dependent rules (fines, overdue) deterministic in tests.
- **Atomic writes** (temp file + `os.replace`) prevent half-written data files.
