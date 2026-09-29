"""CLI entry point: menu-driven interface for the Mini Library Management System."""
import logging
import os

import reports
from book import Book
from exceptions import LibraryError
from library import Library
from storage import JsonStorage

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "library.json")
LOG_FILE = os.path.join(BASE, "library.log")


def ask(msg: str) -> str:
    return input(msg).strip()


def show_books(books):
    print(reports.format_table(["ID", "Title", "Author", "Status"],
                               [(b.book_id, b.title, b.author,
                                 "Available" if b.is_available else f"Issued to {b.issued_to}")
                                for b in books]))


def show_members(members):
    print(reports.format_table(["ID", "Name", "Email", "Books Held"],
                               [(m.member_id, m.name, m.email, len(m.borrowed)) for m in members]))


def book_menu(lib: Library):
    actions = {
        "1": ("Add a book", lambda: print("Added:", lib.add_book(ask("Title: "), ask("Author: ")).book_id)),
        "2": ("View all books", lambda: show_books(lib.view_books())),
        "3": ("Search for a book", lambda: show_books(lib.search_books(ask("Title/author/ID: ")))),
        "4": ("Remove a book", lambda: print("Removed:", lib.remove_book(ask("Book ID: ")).title)),
    }
    run_menu("BOOK MANAGEMENT", actions)


def member_menu(lib: Library):
    actions = {
        "1": ("Add a member", lambda: print("Added:", lib.add_member(ask("Name: "), ask("Email: ")).member_id)),
        "2": ("View members", lambda: show_members(lib.view_members())),
        "3": ("Search for a member", lambda: show_members(lib.search_members(ask("Name/email/ID: ")))),
    }
    run_menu("MEMBER MANAGEMENT", actions)


def issue_menu(lib: Library):
    def issue():
        b = lib.issue_book(ask("Book ID: "), ask("Member ID: "))
        print(f"Issued '{b.title}'. Due on {b.due_date}.")

    def ret():
        fine = lib.return_book(ask("Book ID: "))
        print("Returned." + (f" Late fine: {fine}" if fine else " No fine."))

    def avail():
        bid = ask("Book ID: ")
        print("Available" if lib.check_availability(bid) else "Currently issued")

    run_menu("ISSUE & RETURN", {"1": ("Issue a book", issue), "2": ("Return a book", ret),
                                "3": ("Check availability", avail)})


def report_menu(lib: Library):
    run_menu("REPORTS", {
        "1": ("Available books", lambda: print(reports.available_books_report(lib))),
        "2": ("Issued books", lambda: print(reports.issued_books_report(lib))),
        "3": ("Library summary", lambda: print(reports.summary_report(lib))),
    })


def run_menu(title: str, actions: dict):
    while True:
        print(f"\n=== {title} ===")
        for key, (label, _) in actions.items():
            print(f"  {key}. {label}")
        print("  0. Back")
        choice = ask("Choose: ")
        if choice == "0":
            return
        if choice not in actions:
            print("Invalid choice, try again.")
            continue
        try:
            actions[choice][1]()
        except LibraryError as exc:      # expected, user-facing errors
            print(f"[!] {exc}")
        except (KeyboardInterrupt, EOFError):
            raise
        except Exception:                # unexpected: log full trace, keep app alive
            logging.getLogger(__name__).exception("Unexpected error")
            print("[!] Something went wrong. See library.log for details.")


def main():
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    try:
        lib = Library(JsonStorage(DATA_FILE))
    except LibraryError as exc:
        print(f"[!] Startup failed: {exc}")
        return
    menus = {"1": ("Book Management", book_menu), "2": ("Member Management", member_menu),
             "3": ("Issue & Return", issue_menu), "4": ("Reports", report_menu)}
    try:
        while True:
            print("\n===== MINI LIBRARY MANAGEMENT =====")
            for k, (label, _) in menus.items():
                print(f"  {k}. {label}")
            print("  0. Exit")
            c = ask("Choose: ")
            if c == "0":
                break
            menus[c][1](lib) if c in menus else print("Invalid choice, try again.")
    except (KeyboardInterrupt, EOFError):
        pass
    print("\nGoodbye!")


if __name__ == "__main__":
    main()
