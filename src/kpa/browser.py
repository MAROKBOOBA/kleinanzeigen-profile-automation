from __future__ import annotations

from pathlib import Path
from typing import Any


def expand_path(path: str | Path) -> str:
    return str(Path(path).expanduser().resolve())


def launch_persistent_context(playwright: Any, browser: str, profile_dir: str | Path, headed: bool = False):
    """Launch a persistent browser profile without importing/exporting cookies."""
    profile = Path(profile_dir).expanduser().resolve()
    profile.mkdir(parents=True, exist_ok=True)
    common = {
        "user_data_dir": str(profile),
        "headless": not headed,
        "viewport": {"width": 1280, "height": 900},
        "accept_downloads": False,
    }
    if browser == "chrome":
        return playwright.chromium.launch_persistent_context(channel="chrome", **common)
    if browser == "chromium":
        return playwright.chromium.launch_persistent_context(**common)
    if browser == "firefox":
        return playwright.firefox.launch_persistent_context(**common)
    raise ValueError(f"Unsupported browser: {browser}")
