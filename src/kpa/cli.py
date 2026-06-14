from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

from . import __version__
from .browser import launch_persistent_context
from .filler import fill_listing, finish_mode, is_form_ready, navigate_to_create_form, open_manual_login, screenshot
from .login_guard import LoginAutomationBlocked
from .models import load_listings


def _import_playwright():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SystemExit(
            "Playwright is required for browser commands. Install with: "
            "python -m pip install -e . && python -m playwright install chromium firefox"
        ) from exc
    return sync_playwright


def _default_profile(browser: str) -> str:
    env = os.environ.get("KPA_PROFILE_DIR")
    if env:
        return env
    return f"~/.local/share/kpa/{browser}-profile"


def _add_browser_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--browser", choices=["chrome", "chromium", "firefox"], default=os.environ.get("KPA_BROWSER", "chrome"))
    parser.add_argument("--profile-dir", default="", help="Persistent local browser profile directory")
    parser.add_argument("--headed", action="store_true", help="Show browser window")
    parser.add_argument("--run-dir", default="runs/latest", help="Screenshots/status output directory")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="kpa", description="Credential-safe Kleinanzeigen profile automation")
    parser.add_argument("--version", action="version", version=f"kpa {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    dry = sub.add_parser("dry-run", help="Validate a listing queue without opening a browser")
    dry.add_argument("queue")

    login = sub.add_parser("manual-login", help="Open browser for human login; automation waits passively")
    _add_browser_args(login)
    login.add_argument("--wait-seconds", type=int, default=300)

    check = sub.add_parser("session-check", help="Check whether profile can reach the create-listing form")
    _add_browser_args(check)

    fill = sub.add_parser("fill", help="Fill listings from a queue")
    fill.add_argument("queue")
    _add_browser_args(fill)
    fill.add_argument("--mode", choices=["review", "draft", "publish"], default="review")
    fill.add_argument("--confirm-publish", default="")
    fill.add_argument("--limit", type=int, default=0)
    fill.add_argument("--start", type=int, default=0)
    fill.add_argument("--continue-on-error", action="store_true")

    return parser


def cmd_dry_run(args: argparse.Namespace) -> int:
    listings = load_listings(args.queue)
    payload = {
        "ok": True,
        "items": len(listings),
        "ids": [item.id for item in listings],
        "note": "Dry-run only; no browser opened and no login data read.",
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def _profile(args: argparse.Namespace) -> str:
    return args.profile_dir or _default_profile(args.browser)


def _with_context(args: argparse.Namespace):
    sync_playwright = _import_playwright()
    pw = sync_playwright().start()
    context = None
    try:
        context = launch_persistent_context(pw, args.browser, _profile(args), headed=args.headed)
        page = context.pages[0] if context.pages else context.new_page()
        page.set_default_timeout(5000)
        page.set_default_navigation_timeout(30000)
        yield page
    finally:
        if context is not None:
            context.close()
        pw.stop()


def cmd_manual_login(args: argparse.Namespace) -> int:
    args.headed = True
    for page in _with_context(args):
        ok = open_manual_login(page, wait_seconds=args.wait_seconds)
        print(json.dumps({"ok": ok, "profile_dir": str(Path(_profile(args)).expanduser()), "manual_only": True}, indent=2))
        return 0 if ok else 3
    return 1


def cmd_session_check(args: argparse.Namespace) -> int:
    for page in _with_context(args):
        try:
            navigate_to_create_form(page)
            ready = is_form_ready(page)
            print(json.dumps({"ok": bool(ready), "form_ready": bool(ready), "url": page.url}, ensure_ascii=False, indent=2))
            return 0 if ready else 1
        except LoginAutomationBlocked as exc:
            print(json.dumps({"ok": False, "needs_manual_login": True, "error": str(exc)}, ensure_ascii=False, indent=2))
            return 3


def cmd_fill(args: argparse.Namespace) -> int:
    if args.mode == "publish" and args.confirm_publish != "I_UNDERSTAND":
        raise SystemExit("Publishing requires --confirm-publish I_UNDERSTAND")

    listings = load_listings(args.queue)[args.start:]
    if args.limit > 0:
        listings = listings[: args.limit]

    status = []
    for page in _with_context(args):
        for item in listings:
            try:
                fill_listing(page, item)
                finish_mode(page, mode=args.mode, confirm_publish=args.confirm_publish)
                shot = screenshot(page, args.run_dir, f"{item.id}-{args.mode}") if args.headed else None
                status.append({"id": item.id, "status": args.mode, "screenshot": str(shot) if shot else None})
            except LoginAutomationBlocked as exc:
                status.append({"id": item.id, "status": "needs_manual_login_or_security", "error": str(exc)})
                break
            except Exception as exc:
                status.append({"id": item.id, "status": "error", "error": str(exc)})
                if not args.continue_on_error:
                    break
        print(json.dumps({"ok": all(row["status"] in {"review", "draft", "publish"} for row in status), "items": status}, ensure_ascii=False, indent=2))
        return 0 if all(row["status"] in {"review", "draft", "publish"} for row in status) else 1
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "dry-run":
        return cmd_dry_run(args)
    if args.command == "manual-login":
        return cmd_manual_login(args)
    if args.command == "session-check":
        return cmd_session_check(args)
    if args.command == "fill":
        return cmd_fill(args)
    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
