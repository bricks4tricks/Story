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
