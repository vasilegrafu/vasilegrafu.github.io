# Astro → React migration plan

Source: `D:\Dev.Work\vasilegrafu.github.io_old` (Astro 5 + Tailwind v4).
Target: `webapp/` (Vite 8 + React 19 + TypeScript 6).

Goal: the same site — same pages, content, themes, design system and
architecture rules — rebuilt as a React single-page app, and **deployed to
GitHub Pages automatically every time `main` is pushed**.

`docs/` holds project documentation (this plan, architecture notes, how-tos).
It is never served and never a build output.

## Current state

- `main` on GitHub already contains the scaffold commit; the old Astro
  workflow was removed with it. Nothing deploys today, and Pages still serves
  the last Astro build.
- The framework-free layers are already migrated into `webapp/` (uncommitted):
  profile data, nav items, article registry, theme tokens, routing helper,
  path aliases, static assets (cv.pdf, og.png, robots.txt, favicon), OG image
  source. `npm run build` and `npm run lint` pass.
- Phase 1 (workflow file) and Phase 2 (dependencies installed, without
  Prettier) are done in the working tree, build and lint green. Decisions
  taken on 2026-09-07: push the workflow right away; dependencies approved;
  SEO prerendering later.

## Phase 1 — Deploy on push to `main` (GitHub Actions) — done

Set up the pipeline first, so every later phase ships the moment it lands.

- `.github/workflows/deploy.yml`:
  - Trigger: `push` to `main`, plus `workflow_dispatch` for manual runs.
  - Permissions: `contents: read`, `pages: write`, `id-token: write`;
    concurrency group `pages`, cancel in-progress.
  - **build** job (`working-directory: webapp`): checkout → Node 24 with npm
    cache (matches the local toolchain; Vite 8 needs ≥ 22.12) → `npm ci` →
    `npm run lint` → `npm run build` → `actions/configure-pages` →
    `actions/upload-pages-artifact` with `path: webapp/dist`.
  - **deploy** job: `actions/deploy-pages` into the `github-pages`
    environment, `needs: build`.
- One-time repo setting: **Settings → Pages → Source = GitHub Actions**.
- Vite `base` stays `/` — this is a user site served at the domain root.
- No `.nojekyll` needed: Jekyll only processes branch deploys, not Actions
  artifacts.
- Build output stays in `webapp/dist` (git-ignored). Nothing built is ever
  committed.

How it behaves:

- A commit on its own does nothing; the **push** to `main` triggers the
  workflow. Typical time from push to live: 1–2 minutes.
- If lint or build fails, nothing deploys and the previous release stays
  live. Check the Actions tab after pushing.
- **The first push with this workflow replaces the live Astro site with
  whatever `webapp/` builds at that moment.** Today that is the Vite demo
  page. Either push the workflow only once the site is presentable (after
  Phase 4), or accept a short window with a placeholder. Your call when you
  ask for the commit.

## Phase 2 — Dependencies — done (approved 2026-09-07)

Runtime:

- `react-router` (v8 installed) — client-side routing, `Outlet`, `NavLink`, redirects.
- `tailwindcss` + `@tailwindcss/vite` — same Tailwind v4 the old site used;
  `global.css` ports almost verbatim.
- `lucide-react` — replaces `astro-icon` + `@iconify-json/lucide`.
- `@fontsource-variable/inter`, `@fontsource-variable/space-grotesk` — same
  fonts.

Dev (optional): `prettier` + `prettier-plugin-tailwindcss` — the old repo
formatted with Prettier (single quotes, width 100); the scaffold has no
formatter.

Nothing else. RSS, sitemap, the SPA fallback and the resume PDF need no
packages (Phase 5).

## Phase 3 — Design system and shell — done (2026-09-07)

Design system:

- `src/styles/global.css` ported from the old site: `@import 'tailwindcss'`,
  `@theme` fonts, `@theme inline` token mapping, `@layer components` recipes
  (`.title-*`, `.btn*`, `.card`, `.tag`, `.nav-pill`, `.menu-item`, `.tip`,
  `.prose-article`, …). Only the `astro-icon` bits disappear.
- `index.html`: real `<title>`, description, theme-color, OG/Twitter
  defaults, RSS `<link rel="alternate">`, and the pre-paint theme script
  (`localStorage.theme` → `data-theme` on `<html>`) so there is no flash of
  the wrong theme.
- `main.tsx` imports fonts + `global.css` + `themes/index.css`.
- Remove scaffold styling: `App.css`, `index.css`, `assets/hero.png`,
  `assets/react.svg`, `assets/vite.svg`, `public/icons.svg`.

Shell, in `src/modules/shared/`:

- `BaseLayout.tsx` — header, `<main>`, footer, React Router `<Outlet>`.
- `HeaderPart`, `NavMenuPart`, `MobileMenuPart` (open/close via `useState`),
  `SocialLinksPart`, `FooterPart`.
- `ThemeMenuPart` — dropdown over `themes.ts`; a small `useTheme()` hook
  (own file, hooks only — the `react-refresh` lint rule rejects mixed
  exports) owns `localStorage` + `data-theme`; closes on outside click /
  Escape.

Portable parts, in `src/fx/components/`:

- `IconPart.tsx` — resolves the existing `'lucide:xxx'` string ids from
  `profile.ts` / `nav.ts` to `lucide-react` components, so the data files stay
  untouched.
- `StatTilePart`, `IconCardPart`, `LinkCardPart`, `SegmentBarPart`,
  `FlowDiagramPart`, `MenuButtonPart` — 1:1 ports; `<slot>` becomes
  `children`.

Architecture rules are unchanged (old `ARCHITECTURE.md`): `modules/` (pages
and shared parts), `data/`, `fx/` (portable, content-free), `themes/`,
`styles/global.css`. Imports point downward only; `fx/` imports nothing above
it. Naming: `XxxPage.tsx`, `XxxPart.tsx`, `XxxLayout.tsx`.

Checkpoint: header, footer and theme switching working on an empty page.

## Phase 4 — Pages — done (2026-09-07)

The central route manifest splits in two so the build plugin (Phase 5) can
read it without pulling React into `vite.config.ts`:

- `src/routes.ts` — plain data: path, page module id, whether it is listed in
  the sitemap. No React imports.
- `src/router.tsx` — builds `createBrowserRouter` from that list, pages
  loaded with `React.lazy` so each page is its own chunk. `/resume-print`
  sits outside the `BaseLayout` route (no header/footer); the redirects are
  `<Navigate replace>` elements.

Links in `nav.ts` keep their trailing slashes (`/career/`); React Router
ignores trailing slashes when matching, and `NavLink` supplies the active
state, so `fx/lib/routing.ts` (`isActive`) is probably retired in this phase.

| Route               | Page module                                            | Notes |
| ------------------- | ------------------------------------------------------ | ----- |
| `/`                 | `modules/index/IndexPage.tsx`                          | hero, stats strip, What I do, value props, principles |
| `/career`           | `modules/career/CareerPage.tsx` + `RoleItemPart.tsx`   | stats, era bar, timeline, education, PDF button |
| `/skills`           | `modules/skills/SkillsPage.tsx`                        | |
| `/projects`         | `modules/projects/ProjectsPage.tsx` + `ProjectCardPart.tsx` | flow diagrams |
| `/articles`         | `modules/articles/ArticlesPage.tsx`                    | |
| `/articles/:id`     | `modules/articles/ArticlePage.tsx`                     | content from `content/<id>/ArticlePart.tsx` via `import.meta.glob` |
| `/contact`          | `modules/contact/ContactPage.tsx`                      | |
| `/resume-print`     | `modules/resume-print/ResumePrintPage.tsx`             | no shell; own print CSS; `noindex` |
| `*`                 | `modules/404/NotFoundPage.tsx`                         | |
| `/resume`, `/ideas` | redirects to `/career`, `/`                            | were Astro `redirects` |

Per-page `<title>` / `<meta name="description">` / OG tags: React 19 hoists
these to `<head>` natively — a small `PageMetaPart`, no `react-helmet`.

The one existing article (`why-i-built-this-site`) becomes `ArticlePart.tsx`
+ `CalloutPart.tsx`; its "built with Astro" sentence needs rewording.

Checkpoint per page: visual parity with the old site (old dev server on 4321,
new on 5173, side by side).

## Phase 5 — Static-site concerns a SPA has to solve — done (2026-09-07), prerender left for later

1. **Deep links on GitHub Pages.** Pages serves `404.html` for unknown paths;
   a post-build step copies `index.html` to `404.html` so `/career` loads the
   app and React Router takes over. Small Vite plugin in `vite.config.ts`.
2. **`rss.xml` and `sitemap.xml`.** Generated at build time by the same
   plugin from `registry.ts` and `routes.ts` (Vite bundles the config with
   esbuild, so it can import the TypeScript directly). `robots.txt` updated
   to point at `sitemap.xml` instead of Astro's `sitemap-index.xml`.
3. **Resume PDF.** `/resume-print` stays the print source; regenerate
   `public/cv.pdf` with headless Chrome against `npm run preview`
   (port 4173 instead of 4321). Command documented in the README.
4. **SEO / social previews (optional, later).** A SPA ships an empty
   `<div id="root">` to crawlers. If that matters, add a prerender step using
   `react-dom/static` over the route list at build — no extra dependency, but
   its own piece of work. Recommendation: ship the SPA first.

## Phase 6 — Cleanup and documentation — done (2026-09-07)

- Replace the scaffold `webapp/README.md` with the old README adapted to
  React (dev/build/preview, adding an article, regenerating the PDF, how the
  deploy works).
- Port `ARCHITECTURE.md` (with `.tsx` naming and the React Router manifest)
  into `docs/`, next to this plan.
- Update `CLAUDE.md` section 3 (migration no longer "in progress").
- Delete `App.tsx` demo content once the router is the entry.
- Remove `docs/.gitkeep` now that `docs/` has real content.

## Decisions (taken 2026-09-07)

1. Deploy workflow pushed right away; the Vite placeholder goes live until
   Phase 4 lands.
2. Phase 2 dependencies approved and installed. Prettier left out for now.
3. SEO prerendering: later (Phase 5, item 4 stays optional).

## Order and size

Phase 1 is one small diff. Phases 2–3 are one sitting. Phase 4 is one page
per diff so you can review page by page. Phases 5–6 close it out. Every phase
ends with `npm run build` and `npm run lint` green before it is reported done.
