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

Create a directory in `src/modules/articles/content/` named after the URL slug, with an
`index.mdx` inside:

```
src/modules/articles/content/my-article/
  index.mdx        ← the article (frontmatter + MDX body)
  Chart.astro      ← optional rich content local to this article
  demo.ts          ← components, TypeScript, videos, audio — anything
```

```mdx
---
title: 'Article title'
description: 'One-line summary shown in listings and SEO.'
pubDate: 2026-09-15
tags: ['ai', 'leadership']
---

import Chart from './Chart.astro';

Article body in Markdown… with embedded components: <Chart />
```

Push to `main` and GitHub Actions rebuilds and deploys the site automatically.

## Updating the resume

Profile data (experience, skills, education) lives in `src/data/profile.ts` and feeds the
Career page, plus a print-optimized page at `/resume-print/`
(`src/pages/resume-print.astro`, excluded from the sitemap and marked noindex).

The downloadable PDF at `public/cv.pdf` is printed from that page. After editing
`src/data/profile.ts`, regenerate it with:

```powershell
npm run build
npm run preview   # note the port it prints (4321 unless busy)
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --headless=new --disable-gpu `
  --no-pdf-header-footer --print-to-pdf="<repo>\public\cv.pdf" "http://localhost:4321/resume-print/"
```
