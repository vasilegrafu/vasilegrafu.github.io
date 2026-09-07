# vasilegrafu.github.io

Personal website of **Vasile Grafu** — Engineering Manager, Solutions Architect, Enterprise & AI Systems.

Live at **https://vasilegrafu.github.io**

## Stack

- [Vite](https://vite.dev) + [React 19](https://react.dev) + TypeScript — single-page app
- [React Router](https://reactrouter.com) — client-side routing
- [Tailwind CSS v4](https://tailwindcss.com) — styling, with a themeable token layer
- [Lucide](https://lucide.dev) — icons
- Deployed to GitHub Pages by GitHub Actions on every push to `main`

Architecture notes live in [`../docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md).

## Development

```sh
npm install
npm run dev      # local dev server at http://localhost:5173
npm run build    # type-check + production build to ./dist
npm run lint     # eslint
npm run preview  # preview the production build at http://localhost:4173
```

`npm run build` runs `tsc -b` first, so a type error fails the build. The build
also writes `sitemap.xml`, `rss.xml` and `404.html` (the SPA fallback GitHub
Pages needs for deep links) into `dist/`.

## Adding an article

1. Add the metadata to `src/modules/articles/registry.ts`:

   ```ts
   {
     id: 'my-article',            // the URL slug: /articles/my-article
     title: 'Article title',
     description: 'One-line summary shown in listings, RSS and SEO.',
     pubDate: new Date('2026-09-15'),
     tags: ['ai', 'leadership'],
   }
   ```

2. Create `src/modules/articles/content/my-article/ArticlePart.tsx` exporting a
   default component with the article body. Anything the article needs —
   charts, animations, media, helper components — lives in the same directory.

The listing, the article route, RSS and the sitemap all pick it up from the
registry. Push to `main` and it deploys.

## Updating the resume

Profile data (experience, skills, education, projects) lives in
`src/data/profile.ts` and feeds the Career, Skills and Projects pages, plus a
print-optimised page at `/resume-print` (rendered without the site shell,
`noindex`, not in the sitemap).

The downloadable PDF at `public/cv.pdf` is printed from that page. After editing
`src/data/profile.ts`, regenerate it with:

```powershell
npm run build
npm run preview   # note the port it prints (4173 unless busy)
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --headless=new --disable-gpu `
  --no-pdf-header-footer --print-to-pdf="<repo>\webapp\public\cv.pdf" "http://localhost:4173/resume-print"
```

## Deployment

`.github/workflows/deploy.yml` runs on every push to `main`: install, lint,
build, then publish `webapp/dist` to GitHub Pages. A failing lint or build does
not deploy — the previous release stays live. Check the Actions tab after
pushing.
