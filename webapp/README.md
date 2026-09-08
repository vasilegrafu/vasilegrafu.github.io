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

## Setup

Requires **Node.js 24** (npm 11 ships with it) — the same major the deploy
workflow uses. Everything runs from `webapp/`.

```sh
git clone https://github.com/vasilegrafu/vasilegrafu.github.io.git
cd vasilegrafu.github.io/webapp
npm ci
```

`npm ci` installs exactly what `package-lock.json` pins, which is also what CI
uses. Use `npm install` only when you intend to change dependencies.

## Running locally

```sh
npm run dev      # dev server with hot reload at http://localhost:5173
npm run build    # tsc -b, vite build, then prerender every route into ./dist
npm run preview  # serve ./dist at http://localhost:4173
npm run lint     # eslint
```

The dev server serves the SPA only. Prerendered HTML, `sitemap.xml`, `rss.xml`
and `404.html` are produced by the build, so use `build` + `preview` to check
what GitHub Pages will actually serve. `npm run build` runs `tsc -b` first, so
a type error fails the build. How the prerender and SEO pieces fit together is
in [`../docs/SEO.md`](../docs/SEO.md).

**VS Code.** Open the repository root (not `webapp/`) and the `.vscode/` folder
gives you:

- Tasks (Terminal → Run Task): `webapp: dev`, `webapp: build`, `webapp: lint`,
  `webapp: preview`. `webapp: dev` is the default build task (`Ctrl+Shift+B`).
- Debug (`F5`): *Debug site (Chrome)* / *Debug site (Edge)* start the dev
  server and open the browser with source maps, so breakpoints in `.tsx` files
  work from the editor. *Attach to running dev server* opens the browser only.

Before pushing, run `npm run lint && npm run build` — the deploy workflow runs
the same two steps and does not deploy if either fails.

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

There is no manual deploy step: **every push to `main` is a production
release.** `.github/workflows/deploy.yml` runs `npm ci` → `npm run lint` →
`npm run build`, then publishes `webapp/dist` to GitHub Pages. A failing lint
or build does not deploy — the previous release stays live. Follow the run in
the repository's **Actions** tab; the site is live when the `deploy` job
finishes. The workflow can also be re-run from that tab (*Run workflow*) to
redeploy the current `main` without a new commit.

If a deploy fails, open the run to see which step broke, reproduce with
`npm run lint && npm run build` on the same commit, and push a fix. A newer
push cancels any run still in progress.

**One-time settings** (already done here; only matters for a fork):
*Settings → Pages → Source* must be *GitHub Actions*, and the repository must
be named `<user>.github.io` to be served from the root of
`https://<user>.github.io/` — any other name serves from a sub-path and needs a
Vite `base` setting.

## Troubleshooting

- **`npm ci` fails with a lockfile mismatch** — wrong Node or npm major.
  Install Node 24 and retry.
- **Port 5173 or 4173 already in use** — Vite picks the next free port and
  prints it; the VS Code debug configs assume the defaults, so stop the other
  process or open the printed URL by hand.
- **Looks right in `dev`, wrong on the live site** — check `npm run preview`.
  Prerender and hydration mismatches only show in the built output.
- **Old assets after a deploy** — the app reloads once when it detects a stale
  chunk; a hard refresh (`Ctrl+Shift+R`) clears anything left.
