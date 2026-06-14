# Deutsche Kurzanleitung

Dieses Projekt automatisiert Kleinanzeigen-Formulare nur mit einem bereits vorhandenen oder manuell vorbereiteten lokalen Browserprofil.

## Feste Sicherheitsregel

Die Automatisierung loggt sich niemals selbst ein. Sie speichert und tippt keine Passwörter, 2FA-Codes, Captchas, Telefonnummern, Identitätsdaten, Zahlungsdaten, Cookies, Tokens oder Sessions.

Wenn eine Login-, Sicherheits- oder Account-Prüfung erscheint, stoppt der Lauf. Der Mensch erledigt diesen Schritt selbst.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m playwright install chromium firefox
```

## Beispielablauf

Queue prüfen, ohne Browser zu öffnen:

```bash
kpa dry-run examples/listings.example.json
```

Lokales Profil vorbereiten und manuell einloggen:

```bash
kpa manual-login \
  --browser chrome \
  --profile-dir ~/.local/share/kpa/chrome-profile \
  --wait-seconds 300
```

Session prüfen:

```bash
kpa session-check \
  --browser chrome \
  --profile-dir ~/.local/share/kpa/chrome-profile
```

Formular befüllen und zur Prüfung offen lassen:

```bash
kpa fill examples/listings.example.json \
  --browser chrome \
  --profile-dir ~/.local/share/kpa/chrome-profile \
  --mode review \
  --headed
```

Veröffentlichen ist absichtlich explizit:

```bash
kpa fill examples/listings.example.json \
  --browser chrome \
  --profile-dir ~/.local/share/kpa/chrome-profile \
  --mode publish \
  --confirm-publish I_UNDERSTAND
```

## Was nicht unterstützt wird

- automatischer Login
- Account-Erstellung
- Passwort-/2FA-/Captcha-Automation
- Cookie- oder Session-Export
- Proxy-/Fingerprint-/Stealth-/Anti-Detection-Logik
- Verarbeitung fremder Accounts ohne Berechtigung

## Vor einem Issue

Bitte keine Screenshots oder Logs mit privaten Accountdaten posten. Nutze nur bereinigte Beispiel-Queues und redigierte Logs.
