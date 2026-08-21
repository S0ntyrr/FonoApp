import unittest

from app.security import email_match_filter, normalize_email


class TestEmailCaseInsensitive(unittest.TestCase):
    def test_normalize_email_lowercases_and_strips(self):
        self.assertEqual(normalize_email("  USER@Example.com  "), "user@example.com")

    def test_email_match_filter_is_case_insensitive(self):
        expected = {"email": {"$regex": r"^user@example\.com$", "$options": "i"}}
        self.assertEqual(email_match_filter("USER@Example.com"), expected)


if __name__ == "__main__":
    unittest.main()
