# LogicAndStories

## Building Tailwind CSS

This project uses a PostCSS build pipeline for Tailwind. After installing the
`devDependencies` with `npm install`, run:

```bash
npm run build:css
```

to generate `static/css/styles.css`. You can also run `npm run watch:css` during
development to rebuild on changes.

## Health Check Endpoint

The application exposes a simple health check endpoint at `/health`.
Send a `GET` request to this URL to verify that the server is running.

## Environment Configuration

Configuration values such as database credentials and SMTP settings are read
from environment variables. For local development you can create a `.env` file.

```bash
cp .env.example .env
# then edit .env with your credentials
```

The application automatically loads variables from this file at startup using
`python-dotenv`.

Install Python dependencies including the PostgreSQL driver with:

```bash
pip install -r requirements.txt
```

### PostgreSQL Database

LogicAndStories uses PostgreSQL exclusively via `psycopg2`. Provide a
`DATABASE_URL` connection string or the individual `DB_USER`, `DB_PASSWORD`,
`DB_HOST`, `DB_PORT`, and `DB_NAME` variables. A local PostgreSQL server must be
running for the application and test suite to function correctly.

All Python scripts interact with the database through parameterized queries
using the helpers in `db_utils.py`. This ensures compatibility with PostgreSQL
and guards against SQL injection. The HTML files issue requests to the API
endpoints rather than executing SQL directly.

After pulling the latest code, you can run:

```bash
python add_plan_column.py
```

The signup endpoint now automatically ensures the `plan` column exists, but the
script is provided for manual use when needed.

## Progress Dashboard

Authenticated users can visit `/progress-dashboard.html` to review quiz scores,
completed story modules, and upcoming assignments. Data for the dashboard is
provided by the `/api/dashboard/<user_id>` endpoint.
