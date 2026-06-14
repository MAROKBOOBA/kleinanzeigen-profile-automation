# Contributing

Contributions are welcome if they preserve the safety model.

## Non-negotiable rules

- Do not add automatic login.
- Do not add password, 2FA, captcha, phone, identity, payment, or recovery automation.
- Do not add proxy, fingerprint, stealth, or anti-detection behavior.
- Do not commit real browser profiles, cookies, storage state, screenshots, queues, photos, or personal data.
- Add or update tests when changing login guard behavior.

## Local checks

```bash
python scripts/secret_scan.py .
python -m compileall src scripts
python -m unittest discover -s tests
```
