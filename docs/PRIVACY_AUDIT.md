# Privacy Audit Checklist

Before publishing or releasing:

1. Confirm no browser profiles are committed.
2. Confirm no cookies, storage state, local storage, session storage, SQLite browser databases, screenshots, or run logs are committed.
3. Confirm no real listing queues, photos, addresses, emails, phone numbers, account names, or business/customer data are committed.
4. Run the generic secret scan:

   ```bash
   python scripts/secret_scan.py .
   ```

5. Run a project-specific denylist scan locally for your own names, emails, domains, addresses, postal codes, phone numbers, and internal project names. Do not commit that denylist if it contains private data.

The repository intentionally includes only generic example data.
