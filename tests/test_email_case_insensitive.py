import unittest

from app.security import (
    EMAIL_UNIQUE_INDEX_NAME,
    EMAIL_UNIQUE_INDEX_OPTIONS,
    email_match_filter,
    normalize_email,
)


class TestEmailCaseInsensitive(unittest.TestCase):
    def test_normalize_email_lowercases_and_strips(self):
        self.assertEqual(normalize_email("  USER@Example.com  "), "user@example.com")

    def test_email_match_filter_is_case_insensitive(self):
        expected = {"email": {"$regex": r"^user@example\.com$", "$options": "i"}}
        self.assertEqual(email_match_filter("USER@Example.com"), expected)

    def test_email_unique_index_uses_case_insensitive_collation(self):
        self.assertEqual(EMAIL_UNIQUE_INDEX_NAME, "email_unique_case_insensitive")
        self.assertTrue(EMAIL_UNIQUE_INDEX_OPTIONS["unique"])
        self.assertEqual(EMAIL_UNIQUE_INDEX_OPTIONS["collation"], {"locale": "en", "strength": 2})

    def test_paciente_router_has_email_match_filter_imported(self):
        from app.routers import paciente
        self.assertTrue(callable(getattr(paciente, "email_match_filter", None)))


if __name__ == "__main__":
    unittest.main()
