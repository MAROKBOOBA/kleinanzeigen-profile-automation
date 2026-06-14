# Roadmap

This roadmap focuses on making local, user-consented marketplace form filling safer and easier to maintain.

## v0.1.x — Project hardening

- [x] Publish a credential-safe baseline with no automatic login.
- [x] Add unit tests for login/security detection and queue validation.
- [x] Add a generic secret scanner.
- [x] Add CI for compile, tests, dry-run, and secret scan.
- [ ] Add more sanitized queue examples for common item categories.
- [ ] Document known selectors and fallback behavior without exposing private account data.

## v0.2 — Browser reliability

- [ ] Add selector fixtures for form fields where possible.
- [ ] Add non-network tests for page-guard behavior using fake page objects.
- [ ] Improve structured status output for review/draft/publish runs.
- [ ] Add clearer error codes for manual-login, security-stop, validation, and selector failure.

## v0.3 — Maintainer workflow automation

- [ ] Add changelog/release automation.
- [ ] Add issue triage labels and examples.
- [ ] Add a public maintainer guide for safe selector updates.
- [ ] Add optional telemetry-free debug bundles that redact sensitive content by default.

## Explicit non-goals

The project will not implement automatic login, credential typing, 2FA/captcha handling, account creation, cookie/session export, proxy rotation, fingerprinting, stealth, or detection evasion.
