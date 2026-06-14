# No-Login-Automation Policy

This project is built for existing, user-owned browser sessions. Login is always manual.

## Hard rule

The automation must never type, submit, store, replay, import, export, or infer:

- passwords or passkeys,
- email/password login combinations,
- 2FA, TOTP, SMS, recovery codes,
- captchas,
- phone, identity, payment, or account recovery data,
- cookies, tokens, local-storage sessions, or browser profile contents.

## Allowed login flow

`kpa manual-login` may open a visible browser window using a local persistent profile and wait passively. The human account owner performs login and any challenge manually. The tool only observes whether the page leaves the login/security flow.

## Required stop conditions

The run stops if the page appears to contain:

- login or signup flow,
- password field,
- one-time-code field,
- captcha/security challenge,
- phone/identity/payment prompt,
- account warning or temporary block.

## Why this exists

This keeps the project usable for legitimate assisted form-filling while avoiding credential collection, account takeover risk, captcha bypass, and anti-detection behavior.
