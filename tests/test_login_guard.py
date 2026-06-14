import unittest

from kpa.login_guard import (
    LoginAutomationBlocked,
    assert_field_name_is_safe,
    contains_login_or_security_signal,
    forbidden_sensitive_keys,
    redact,
)


class LoginGuardTests(unittest.TestCase):
    def test_login_detected_by_url(self):
        self.assertTrue(contains_login_or_security_signal(url="https://www.kleinanzeigen.de/m-einloggen-sso.html"))

    def test_security_detected_by_text(self):
        self.assertTrue(contains_login_or_security_signal(body_text="Bitte Passwort eingeben"))
        self.assertTrue(contains_login_or_security_signal(body_text="Captcha Sicherheitsprüfung"))

    def test_normal_listing_page_not_detected(self):
        self.assertFalse(
            contains_login_or_security_signal(
                url="https://www.kleinanzeigen.de/p-anzeige-aufgeben.html",
                title="Anzeige aufgeben",
                body_text="Titel Preis Beschreibung",
            )
        )

    def test_forbidden_sensitive_keys_nested(self):
        raw = {"title": "x", "account": {"session_token": "secret"}}
        self.assertEqual(forbidden_sensitive_keys(raw), {"account.session_token"})

    def test_redact_common_secret_assignments(self):
        self.assertNotIn("supersecret", redact("password=supersecret"))
        token = "abcdef" + "012345678901234567890123456789"
        self.assertNotIn("abcdef", redact("Bearer " + token))

    def test_refuses_sensitive_field_names(self):
        with self.assertRaises(LoginAutomationBlocked):
            assert_field_name_is_safe("password")


if __name__ == "__main__":
    unittest.main()
