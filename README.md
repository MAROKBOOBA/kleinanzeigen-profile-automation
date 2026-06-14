# Kleinanzeigen Profile Automation

Assisted Kleinanzeigen browser automation for people who already have a logged-in Firefox, Chromium, or Google Chrome profile — or who want to complete login manually once and then reuse that local browser profile.

The repository is intentionally designed around one hard rule:

> **No automatic login. No stored passwords. No 2FA/captcha/identity/payment automation.**

If a login, password, 2FA, captcha, phone, identity, payment, or security prompt appears, the run stops and asks the human to handle it manually.

## What this project does

- Loads listing data from JSON, YAML, or CSV.
- Opens Kleinanzeigen in a persistent local browser profile.
- Supports Firefox, bundled Chromium, and Google Chrome via Playwright.
- Can fill listing forms for review/draft/publish workflows.
- Leaves login and account-security steps to the account owner.
- Refuses sensitive credential/session fields in listing input.
- Keeps example data generic and does not require personal configuration files.

## What this project does **not** do

- No automatic login.
- No password, passkey, 2FA, captcha, phone, identity, payment, or recovery handling.
- No cookie theft/import/export.
- No proxy/fingerprint/stealth/anti-detection logic.
- No scraping of private account data.
- No bundled personal browser profile, cookies, tokens, listings, photos, or user data.

Use it only with accounts you own or are authorized to operate, and follow marketplace rules and local law.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m playwright install chromium firefox
```

Google Chrome support uses the locally installed Chrome through Playwright's `channel=chrome`.

## Quick start

Dry-run a listing queue without opening a browser:

```bash
kpa dry-run examples/listings.example.json
```

Create or reuse a **dedicated** browser profile and log in manually:

```bash
kpa manual-login \
  --browser chrome \
  --profile-dir ~/.local/share/kpa/chrome-profile \
  --wait-seconds 300
```

Check that the profile can reach the create-listing form without login:

```bash
kpa session-check \
  --browser chrome \
  --profile-dir ~/.local/share/kpa/chrome-profile
```

Fill the form and stop for human review:

```bash
kpa fill examples/listings.example.json \
  --browser chrome \
  --profile-dir ~/.local/share/kpa/chrome-profile \
  --mode review \
  --headed
```

Publish is deliberately explicit:

```bash
kpa fill examples/listings.example.json \
  --browser chrome \
  --profile-dir ~/.local/share/kpa/chrome-profile \
  --mode publish \
  --confirm-publish I_UNDERSTAND
```

## Firefox notes

Firefox support uses a persistent Playwright Firefox profile:

```bash
kpa manual-login --browser firefox --profile-dir ~/.local/share/kpa/firefox-profile --wait-seconds 300
kpa fill examples/listings.example.json --browser firefox --profile-dir ~/.local/share/kpa/firefox-profile --mode review --headed
```

For privacy and stability, do not point automation at a live daily browser profile while that browser is open. Prefer a dedicated profile that you manually log in to.

## Listing input

See `examples/listings.example.json`.

Required fields:

- `title`
- `price`
- `description`

Optional fields:

- `postal_code`
- `city`
- `condition`
- `category_path`
- `shipping`
- `photos` (not required; photo upload is not performed unless you extend the project yourself)

Sensitive keys such as `password`, `passwort`, `otp`, `2fa`, `token`, `cookie`, and `session` are rejected.

## Safety architecture

The login ban is enforced in code:

- `kpa.login_guard` detects login/security pages by URL, title, body text, and sensitive form controls.
- The filler calls the guard before form actions.
- Input loading rejects credential/session-like keys.
- `manual-login` opens the browser and waits passively. It does not type or submit credentials.
- `publish` requires `--confirm-publish I_UNDERSTAND`.

Details: `docs/LOGIN_POLICY.md`.

## Privacy checks before publishing

Run:

```bash
python scripts/secret_scan.py .
python -m compileall src scripts
python -m unittest discover -s tests
```

This repository should contain only source code, documentation, and generic example data. Browser profiles, logs, run artifacts, screenshots, cookies, storage state files, `.env` files, and local queues are ignored by `.gitignore`.

## Repository status for OSS applications

This is a new open-source project template. For programs that evaluate OSS impact, add evidence over time:

- public issues and roadmap,
- releases,
- documentation improvements,
- external users/stars/forks,
- real maintainer activity,
- examples and test coverage.

## License

MIT. See `LICENSE`.
