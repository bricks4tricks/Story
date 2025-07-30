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
