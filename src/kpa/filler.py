from __future__ import annotations

import time
from pathlib import Path
from typing import Iterable

from .login_guard import LoginAutomationBlocked, assert_field_name_is_safe, ensure_safe_page
from .models import Listing

CREATE_URL = "https://www.kleinanzeigen.de/p-anzeige-aufgeben.html"
LOGIN_HANDOFF_URL = "https://www.kleinanzeigen.de/m-einloggen-sso.html?targetUrl=/p-anzeige-aufgeben.html"


def _regex(text: str):
    import re

    return re.compile(re.escape(text), re.IGNORECASE)


def _click(locator, timeout_ms: int = 1500) -> bool:
    try:
        locator.first.click(timeout=timeout_ms)
        return True
    except Exception:
        return False


def click_any_text(page, texts: Iterable[str], timeout_ms: int = 1500) -> bool:
    for text in texts:
        pattern = _regex(text)
        for role in ("button", "link", "radio", "checkbox", "option"):
            if _click(page.get_by_role(role, name=pattern), timeout_ms=timeout_ms):
                return True
        if _click(page.get_by_text(pattern), timeout_ms=timeout_ms):
            return True
    return False


def accept_cookies_if_present(page) -> None:
    click_any_text(page, ["Alle akzeptieren", "Akzeptieren", "Einverstanden", "OK", "Okay"], timeout_ms=800)


def fill_first(page, field_name: str, value: str, labels: list[str], selectors: list[str]) -> bool:
    assert_field_name_is_safe(field_name)
    ensure_safe_page(page)
    for label in labels:
        try:
            page.get_by_label(_regex(label)).first.fill(str(value), timeout=2500)
            return True
        except Exception:
            pass
    for selector in selectors:
        try:
            page.locator(selector).first.fill(str(value), timeout=2500)
            return True
        except Exception:
            pass
    return False


def is_form_ready(page) -> bool:
    try:
        return page.get_by_label(_regex("Titel")).first.is_visible(timeout=800)
    except Exception:
        pass
    for selector in ("input[name*='title' i]", "input[id*='title' i]", "textarea[name*='description' i]"):
        try:
            if page.locator(selector).first.is_visible(timeout=800):
                return True
        except Exception:
            pass
    return False


def wait_for_manual_login(page, wait_seconds: int) -> bool:
    deadline = time.time() + max(1, int(wait_seconds))
    while time.time() < deadline:
        try:
            ensure_safe_page(page)
            if is_form_ready(page):
                return True
            # If no login/security signal remains, consider the handoff complete.
            return True
        except LoginAutomationBlocked:
            time.sleep(2)
    return False


def open_manual_login(page, wait_seconds: int) -> bool:
    page.goto(LOGIN_HANDOFF_URL, wait_until="domcontentloaded")
    accept_cookies_if_present(page)
    return wait_for_manual_login(page, wait_seconds=wait_seconds)


def navigate_to_create_form(page) -> None:
    page.goto(CREATE_URL, wait_until="domcontentloaded")
    accept_cookies_if_present(page)
    ensure_safe_page(page)


def select_category_if_possible(page, listing: Listing) -> None:
    if not listing.category_path:
        return
    for part in listing.category_path:
        ensure_safe_page(page)
        if not click_any_text(page, [part], timeout_ms=2000):
            break
        time.sleep(0.3)
    click_any_text(page, ["Weiter", "Fortfahren"], timeout_ms=1200)


def set_condition_if_possible(page, listing: Listing) -> None:
    if not listing.condition:
        return
    ensure_safe_page(page)
    for selector in ("select[name*='condition' i]", "select[id*='condition' i]"):
        try:
            page.locator(selector).first.select_option(label=listing.condition, timeout=1200)
            return
        except Exception:
            pass
    if click_any_text(page, ["Zustand auswählen", "Zustand", "Bitte wählen"], timeout_ms=1200):
        time.sleep(0.3)
        click_any_text(page, [listing.condition], timeout_ms=1200)
        click_any_text(page, ["Bestätigen", "Übernehmen", "Speichern"], timeout_ms=1200)


def fill_listing(page, listing: Listing) -> None:
    navigate_to_create_form(page)
    select_category_if_possible(page, listing)

    if not fill_first(
        page,
        "title",
        listing.title,
        labels=["Titel"],
        selectors=["input[name*='title' i]", "input[id*='title' i]", "input[placeholder*='Titel' i]"],
    ):
        raise RuntimeError("Could not fill title")

    if not fill_first(
        page,
        "price",
        listing.price,
        labels=["Preis"],
        selectors=["input[name*='price' i]", "input[id*='price' i]", "input[placeholder*='Preis' i]"],
    ):
        raise RuntimeError("Could not fill price")

    if not fill_first(
        page,
        "description",
        listing.description,
        labels=["Beschreibung"],
        selectors=[
            "textarea[name*='description' i]",
            "textarea[id*='description' i]",
            "textarea[placeholder*='Beschreibung' i]",
            "textarea",
        ],
    ):
        raise RuntimeError("Could not fill description")

    if listing.postal_code:
        fill_first(
            page,
            "postal_code",
            listing.postal_code,
            labels=["PLZ", "Postleitzahl"],
            selectors=["input[name*='zip' i]", "input[name*='postal' i]", "input[placeholder*='PLZ' i]"],
        )
    if listing.city:
        fill_first(
            page,
            "city",
            listing.city,
            labels=["Ort"],
            selectors=["input[name*='city' i]", "input[id*='city' i]", "input[placeholder*='Ort' i]"],
        )

    set_condition_if_possible(page, listing)
    ensure_safe_page(page)


def finish_mode(page, mode: str, confirm_publish: str = "") -> None:
    ensure_safe_page(page)
    if mode == "review":
        return
    if mode == "draft":
        if not click_any_text(page, ["Entwurf speichern", "Speichern"], timeout_ms=4000):
            raise RuntimeError("Could not find draft/save button")
        return
    if mode == "publish":
        if confirm_publish != "I_UNDERSTAND":
            raise RuntimeError("Publishing requires --confirm-publish I_UNDERSTAND")
        if not click_any_text(page, ["Anzeige aufgeben", "Veröffentlichen", "Inserat aufgeben"], timeout_ms=4000):
            raise RuntimeError("Could not find publish button")
        return
    raise ValueError(f"Unsupported mode: {mode}")


def screenshot(page, run_dir: str | Path, name: str) -> Path:
    path = Path(run_dir).expanduser().resolve()
    path.mkdir(parents=True, exist_ok=True)
    out = path / f"{name}.png"
    page.screenshot(path=str(out), full_page=True)
    return out
