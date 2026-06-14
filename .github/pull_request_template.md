# Pull Request Checklist

Thanks for contributing. Keep the project credential-safe and local-profile focused.

## Summary

- 

## Safety checklist

- [ ] This PR does not automate login, password, passkey, 2FA, captcha, phone, identity, payment, recovery, cookie, token, or session handling.
- [ ] This PR does not add proxy, fingerprint, stealth, or anti-detection behavior.
- [ ] This PR does not commit browser profiles, cookies, storage state, screenshots, private listing queues, logs, photos, or personal data.
- [ ] Login/security/account-warning pages still stop automation.

## Verification

- [ ] `python -m compileall -q src scripts`
- [ ] `PYTHONPATH=src python -m unittest discover -s tests`
- [ ] `PYTHONPATH=src python -m kpa dry-run examples/listings.example.json`
- [ ] `python scripts/secret_scan.py .`
