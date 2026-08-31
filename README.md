# vasilegrafu.github.io

Personal website of **Vasile Grafu** — Engineering Manager, Solutions Architect, Enterprise & AI Systems.

Live at **https://vasilegrafu.github.io**

## Stack

- [Astro](https://astro.build) — static site generator
- [Tailwind CSS v4](https://tailwindcss.com) — styling
- Markdown content collections for articles
- Deployed to GitHub Pages via GitHub Actions on every push to `main`

## Development

```sh
npm install
npm run dev      # local dev server at http://localhost:4321
npm run build    # production build to ./dist
npm run preview  # preview the production build
```

## Adding an article

Create a Markdown file in `src/content/articles/` with frontmatter:

```md
---
title: 'Article title'
description: 'One-line summary shown in listings and SEO.'
pubDate: 2026-09-15
tags: ['ai', 'leadership']
---

Article body in Markdown…
```

Push to `main` and GitHub Actions rebuilds and deploys the site automatically.

## Updating the resume

Profile data (experience, skills, education) lives in `src/data/profile.ts` and feeds the
Career and Resume pages. The downloadable PDF is generated from `tools/resume-print.html`
(see instructions in that file) and stored at `public/cv.pdf`.
