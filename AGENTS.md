# AGENTS Instructions

This repository is deployed on **Render** and uses **PostgreSQL** via `psycopg2`.
When modifying database code:
- Keep queries compliant with PostgreSQL syntax.
- Use `psycopg2.sql` helpers for dynamic SQL when needed.
- Prefer connection helpers in `db_utils.py`.

Before committing any changes run the test suite:
```bash
pytest -q
```

Python code should follow standard style (4-space indentation).
