# Architecture

All paths are relative to `webapp/`.

## Layers

```
src/
├─ modules/            application layer
│  ├─ shared/          cross-module parts, BaseLayout, nav data, page metadata
│  ├─ index/ career/ … one directory per page
│  └─ articles/        listing + article page; content/<id>/ per article
├─ data/               content layer (profile.ts — the site's facts)
├─ fx/                 framework layer — portable to any project
│  ├─ components/      fully prop-driven parts (no site content)
│  └─ lib/             pure functions
├─ styles/global.css   design system (token mapping + Tailwind recipes)
├─ themes/             design tokens — one CSS file per look + themes.ts registry
├─ routes.ts           central route manifest (URL → page id), plain data
├─ routeTree.tsx       route objects built from the manifest (lazy pages)
├─ router.tsx          the browser router
├─ prerender.tsx       build-time rendering of a route to HTML
└─ main.tsx            entry: fonts, global.css, hydrate or render
scripts/prerender.ts   post-build step writing one HTML file per route into dist/
```

**Dependency rule: imports point downward only.**
Modules may use `shared`, `@fx`, `@data`, `@themes`, and design classes.
`fx/` may import **nothing** above it — no profile data, no nav, no theme files
(theme tokens reach it only as CSS variables at runtime).

Path aliases (`tsconfig.app.json`, mirrored in `vite.config.ts`): `@modules/*`,
`@fx/*`, `@data/*`, `@themes/*`, `@styles/*`.

## Naming

- `XxxPage.tsx` — a page (registered in `routes.ts` + `router.tsx`).
- `XxxPart.tsx` — a reusable component.
- `XxxLayout.tsx` — a layout (`modules/shared/BaseLayout.tsx`).
- `useXxx.ts` — a hook, in its own file (the `react-refresh` lint rule rejects
  files that export both components and non-components).
- A part used by one page lives in that page's module; used by several, in
  `modules/shared/`; usable by other projects, in `fx/components/`.

## Routing

`src/routes.ts` is the single list of URLs: `path`, `page` id, whether it is in
the sitemap, and whether it renders `bare` (outside the shell — the resume
print page). It has no React imports, so the build plugin in `vite.config.ts`
can read it too. `src/routeTree.tsx` maps each page id to a `React.lazy`
import and builds the route objects; `src/router.tsx` turns them into
`createBrowserRouter` for the browser and `src/prerender.tsx` into a static
router for the build. Every page is its own chunk.

Adding a page = new module directory + one entry in `routes.ts` + one lazy
import in `routeTree.tsx`.

Internal links use `<Link>`/`<NavLink>` from React Router and the
no-trailing-slash form (`/career`). `PageMetaPart` normalises the canonical
URL to that form whichever way the page was reached.

## Head metadata

`modules/shared/PageMetaPart.tsx` renders `<title>`, description, canonical and
Open Graph tags; React 19 hoists them into `<head>`. Every page renders one.
Site-wide, page-independent tags (icon, theme-color, OG image, RSS link) and the
pre-paint theme script live in `index.html`.

## Styling ladder

1. **Tokens** (`src/themes/*.css`) — a theme is ~24 `--t-*` values; the token
   contract is documented in `themes/index.css`. `@theme inline` in
   `global.css` exposes them as utilities (`bg-bg`, `text-ink`, `text-accent`…).
   Never write a raw palette color (`slate-600`, `indigo-500`) in a component.
2. **Recipes** (`global.css` `@layer components`) — named classes for repeated
   patterns: `.title-*`, `.btn*`, `.card`, `.tag`, `.badge`, `.chip`,
   `.nav-pill`, `.menu-item`, `.icon-tile`, `.tip`, `.lede`, `.prose-article`…
   Extract a recipe only when a pattern repeats or has a clear name.
3. **Inline utilities** — everything else, directly in the markup. Conditional
   classes go through `cx()` from `@fx/lib/cx`.
4. **`style=` attribute** — only for data-driven values Tailwind cannot know
   (e.g. `SegmentBarPart` widths, theme swatches).
5. **Component-local stylesheets — only one.** `modules/resume-print/resume-print.css`
   is deliberately theme-independent print CSS, scoped under `.resume-print`.

## Icons

Content files name icons as `'lucide:<kebab-name>'`. `fx/components/IconPart.tsx`
resolves those to `lucide-react` components from an explicit registry, so only
the icons in use are bundled. GitHub and LinkedIn are drawn inline there
(Lucide no longer ships brand icons). Adding an icon = one import + one
registry line.

## Articles

`modules/articles/registry.ts` lists metadata; each article is a directory
`modules/articles/content/<id>/` with `ArticlePart.tsx` (plus any local
components, scripts or media). `ArticlePage` resolves the content by
convention with `import.meta.glob`; listing, RSS and sitemap read the registry.

## Themes

Adding a theme: create `src/themes/<name>.css` implementing the token
contract, import it in `themes/index.css`, add an entry in `themes.ts` — it
appears in the header dropdown automatically. Selection persists in
`localStorage` (`useTheme`) and is applied pre-paint by the inline script in
`index.html`; without a selection, light is the default.

## Build outputs beyond the app

The `static-site-files` plugin in `vite.config.ts` emits, at build time:

- `sitemap.xml` — every route flagged `sitemap: true`, with `/articles/:id`
  expanded from the registry.
- `rss.xml` — the article feed.
- `404.html` — a copy of the empty `index.html` shell, so GitHub Pages serves
  the app for unknown URLs and the router renders the 404 page.

Then `scripts/prerender.ts` writes a static HTML file for every real route
(`career.html` + `career/index.html`, …), which the client hydrates. The
reasoning and the rules that keep it working are in [SEO.md](SEO.md).
