import os
import sys
import tempfile
import unittest
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import reports
from exceptions import *
from library import Library
from storage import JsonStorage


class LibraryTests(unittest.TestCase):
    def setUp(self):
        self.lib = Library()
        self.b = self.lib.add_book("Clean Code", "Robert Martin")
        self.m = self.lib.add_member("Animesh", "animesh@example.com")

    # Module 1
    def test_add_and_auto_ids(self):
        b2 = self.lib.add_book("Refactoring", "Martin Fowler")
        self.assertEqual((self.b.book_id, b2.book_id), ("B001", "B002"))

    def test_add_book_validation_and_duplicate(self):
        with self.assertRaises(ValidationError): self.lib.add_book("  ", "X")
        with self.assertRaises(DuplicateError): self.lib.add_book("clean code", "robert martin")

    def test_search_case_insensitive(self):
        self.assertEqual(len(self.lib.search_books("CLEAN")), 1)
        self.assertEqual(self.lib.search_books("nothing"), [])

    def test_remove_book(self):
        self.lib.remove_book("b001")
        with self.assertRaises(BookNotFoundError): self.lib.get_book("B001")

    def test_cannot_remove_issued_book(self):
        self.lib.issue_book("B001", "M001")
        with self.assertRaises(BookNotAvailableError): self.lib.remove_book("B001")

    # Module 2
    def test_member_validation_and_duplicate(self):
        with self.assertRaises(ValidationError): self.lib.add_member("Bob", "not-an-email")
        with self.assertRaises(DuplicateError): self.lib.add_member("Other", "ANIMESH@example.com")

    def test_search_member(self):
        self.assertEqual(self.lib.search_members("anim")[0].member_id, "M001")

    # Module 3
    def test_issue_and_return_on_time(self):
        self.lib.issue_book("B001", "M001")
        self.assertFalse(self.lib.check_availability("B001"))
        self.assertEqual(self.lib.return_book("B001"), 0)
        self.assertTrue(self.lib.check_availability("B001"))
        self.assertEqual(self.m.borrowed, [])

    def test_double_issue_rejected(self):
        self.lib.issue_book("B001", "M001")
        with self.assertRaises(BookNotAvailableError): self.lib.issue_book("B001", "M001")

    def test_late_fine(self):
        start = date(2026, 1, 1)
        self.lib.issue_book("B001", "M001", today=start)
        fine = self.lib.return_book("B001", today=start + timedelta(days=Library.LOAN_DAYS + 5))
        self.assertEqual(fine, 5 * Library.FINE_PER_DAY)

    def test_member_limit(self):
        for i in range(Library.MAX_BOOKS_PER_MEMBER + 1):
            self.lib.add_book(f"Book {i}", "A")
        for i in range(2, 2 + Library.MAX_BOOKS_PER_MEMBER):
            self.lib.issue_book(f"B{i:03d}", "M001")
        with self.assertRaises(IssueLimitError): self.lib.issue_book("B001", "M001")

    def test_return_not_issued(self):
        with self.assertRaises(NotIssuedError): self.lib.return_book("B001")

    def test_unknown_ids(self):
        with self.assertRaises(MemberNotFoundError): self.lib.issue_book("B001", "M999")
        with self.assertRaises(BookNotFoundError): self.lib.issue_book("B999", "M001")

    # Module 4
    def test_reports(self):
        self.lib.add_book("Refactoring", "Martin Fowler")
        self.lib.issue_book("B001", "M001", today=date(2026, 1, 1))
        s = reports.summary_data(self.lib, today=date(2026, 3, 1))
        self.assertEqual(s, {"total_books": 2, "available": 1, "issued": 1, "members": 1, "overdue": 1})
        self.assertIn("Refactoring", reports.available_books_report(self.lib))
        self.assertIn("OVERDUE", reports.issued_books_report(self.lib, today=date(2026, 3, 1)))

    # Persistence
    def test_persistence_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "lib.json")
            lib = Library(JsonStorage(path))
            lib.add_book("Dune", "Frank Herbert"); lib.add_member("Sam", "sam@x.com")
            lib.issue_book("B001", "M001")
            lib2 = Library(JsonStorage(path))
            self.assertFalse(lib2.get_book("B001").is_available)
            self.assertEqual(lib2.get_member("M001").borrowed, ["B001"])

    def test_corrupt_file_raises_storage_error(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "bad.json")
            with open(path, "w") as f:
                f.write("{not json")
            with self.assertRaises(StorageError): Library(JsonStorage(path))


if __name__ == "__main__":
    unittest.main()
