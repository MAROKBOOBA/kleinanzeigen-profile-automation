from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any


class LoginAutomationBlocked(RuntimeError):
    """Raised when the browser appears to be in a login/security flow."""


LOGIN_URL_MARKERS = (
    "auth.kleinanzeigen",
    "m-einloggen",
    "login",
    "signin",
    "sign-in",
    "anmelden",
    "einloggen",
    "registrieren",
)

SECURITY_TEXT_MARKERS = (
    "passwort",
    "password",
    "einloggen",
    "anmelden",
    "login",
    "captcha",
    "sicherheits",
    "security check",
    "2fa",
    "two-factor",
    "one-time code",
    "bestätigungscode",
    "telefonnummer",
    "phone number",
    "identity",
    "identität",
    "zahlung",
    "payment",
    "recovery code",
    "konto eingeschränkt",
    "vorübergehend gesperrt",
)

SENSITIVE_FIELD_SELECTORS = (
    "input[type='password']",
    "input[name*='password' i]",
    "input[id*='password' i]",
    "input[name*='passwort' i]",
    "input[id*='passwort' i]",
    "input[name*='otp' i]",
    "input[id*='otp' i]",
    "input[name*='totp' i]",
    "input[id*='totp' i]",
    "input[name*='captcha' i]",
    "input[id*='captcha' i]",
    "input[name*='2fa' i]",
    "input[id*='2fa' i]",
    "input[name*='code' i]",
    "input[id*='code' i]",
)

FORBIDDEN_INPUT_KEYS = (
    "password",
    "passwort",
    "passwd",
    "passkey",
    "secret",
    "token",
    "cookie",
    "cookies",
    "session",
    "storage_state",
    "local_storage",
    "otp",
    "totp",
    "2fa",
    "mfa",
    "captcha",
    "recovery",
    "payment",
    "identity",
)

_REDACT_PATTERNS = (
    re.compile(r"(?i)(password|passwort|token|secret|cookie|session)\s*[:=]\s*[^\s,;]+"),
    re.compile(r"(?i)(bearer\s+)[a-z0-9._\-]+"),
)


def redact(text: str) -> str:
    out = str(text)
    for pattern in _REDACT_PATTERNS:
        out = pattern.sub(lambda m: m.group(1) + "[REDACTED]", out)
    return out


def _flat_text(*parts: Any) -> str:
    return " ".join(str(part or "").lower() for part in parts)


def contains_login_or_security_signal(url: str = "", title: str = "", body_text: str = "") -> bool:
    url_l = (url or "").lower()
    if any(marker in url_l for marker in LOGIN_URL_MARKERS):
        return True
    haystack = _flat_text(title, body_text)
    return any(marker in haystack for marker in SECURITY_TEXT_MARKERS)


def forbidden_sensitive_keys(raw: Mapping[str, Any], prefix: str = "") -> set[str]:
    found: set[str] = set()
    for key, value in raw.items():
        key_text = str(key).lower()
        dotted = f"{prefix}.{key_text}" if prefix else key_text
        if any(marker in key_text for marker in FORBIDDEN_INPUT_KEYS):
            found.add(dotted)
        if isinstance(value, Mapping):
            found.update(forbidden_sensitive_keys(value, prefix=dotted))
    return found


def _locator_visible(page: Any, selector: str) -> bool:
    try:
        locator = page.locator(selector)
        return bool(locator.first.is_visible(timeout=500))
    except Exception:
        return False


def ensure_safe_page(page: Any) -> None:
    """Raise if the current page looks like login/account-security UI.

    This function is intentionally conservative. False positives are safer than
    accidentally interacting with credentials or account challenges.
    """
    url = getattr(page, "url", "") or ""
    try:
        title = page.title(timeout=1000) or ""
    except Exception:
        title = ""
    try:
        body_text = page.locator("body").inner_text(timeout=1000)[:3000]
    except Exception:
        body_text = ""

    if contains_login_or_security_signal(url=url, title=title, body_text=body_text):
        raise LoginAutomationBlocked(
            "Login/security flow detected. Stop automation and complete this step manually."
        )

    for selector in SENSITIVE_FIELD_SELECTORS:
        if _locator_visible(page, selector):
            raise LoginAutomationBlocked(
                f"Sensitive credential/challenge field detected ({selector}). Stop automation."
            )


def assert_field_name_is_safe(field_name: str) -> None:
    field = field_name.lower()
    if any(marker in field for marker in FORBIDDEN_INPUT_KEYS):
        raise LoginAutomationBlocked(f"Refusing to fill sensitive field: {field_name}")
