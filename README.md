# vasilegrafu.github.io

Source of my personal website, live at **https://vasilegrafu.github.io**.

I'm **Vasile Grafu** — Engineering Manager, Solutions Architect, Enterprise &
AI Systems. The site is where I keep my career story, skills, selected projects
and the occasional article, plus a printable resume.

## What's here

```
webapp/    the site — Vite + React 19 + TypeScript, deployed to GitHub Pages
docs/      how it is built: architecture notes and the SEO/prerender setup
.vscode/   VS Code tasks and debug configs for running it locally
.github/   the workflow that builds and publishes on every push to main
```

## Where to go next

- **Run or change the site** → [`webapp/README.md`](webapp/README.md): setup,
  local dev, adding an article, updating the resume, deployment.
- **Understand the code** → [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md):
  layers, naming, styling rules and themes.
- **Prerendering, sitemap, RSS, social previews** →
  [`docs/SEO.md`](docs/SEO.md).

## How it ships

The site is a single-page React app. At build time every route is prerendered
to static HTML so search engines and link previews see real content; in the
browser it hydrates and routes client-side. A GitHub Actions workflow builds
`webapp/` and publishes it to GitHub Pages on every push to `main`, so the
`main` branch is always what's live.

## Using this as a template

Fork it, replace the content in `webapp/src/data/profile.ts` and the articles
under `webapp/src/modules/articles/content/`, and name your fork
`<your-user>.github.io`. The site content is mine; the code you're welcome to
learn from and reuse.
