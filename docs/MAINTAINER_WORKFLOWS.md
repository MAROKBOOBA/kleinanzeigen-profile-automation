# Maintainer Workflows

This document explains how maintainers should evolve the project without weakening the safety model.

## Standard check sequence

Run before every commit:

```bash
python -m compileall -q src scripts
PYTHONPATH=src python -m unittest discover -s tests
PYTHONPATH=src python -m kpa dry-run examples/listings.example.json
python scripts/secret_scan.py .
```

## Safe selector updates

1. Reproduce the failure with a sanitized queue.
2. Do not post screenshots or HTML containing private account data.
3. Patch selectors conservatively.
4. Add or update unit tests for safety behavior if a login/security guard path changed.
5. Verify that login/security pages still stop automation.

## Issue triage labels

Recommended labels:

- `bug` — reproducible implementation problem.
- `enhancement` — requested improvement within safety policy.
- `safety` — login/security/privacy guard behavior.
- `documentation` — docs-only improvement.
- `selector` — form selector maintenance.
- `needs-triage` — maintainer has not reviewed yet.
- `blocked-policy` — request conflicts with non-goals.

## Release checklist

1. Update `CHANGELOG.md`.
2. Run the standard checks.
3. Ensure CI is green on `main`.
4. Tag with `vX.Y.Z`.
5. Create a GitHub release with verification notes.
