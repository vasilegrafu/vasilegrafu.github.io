# Architecture

## Layers

```
src/
├─ modules/            application layer
│  ├─ shared/          cross-module parts, BaseLayout, nav data
│  ├─ index/ career/ … one directory per page
│  └─ …
├─ data/               content layer (profile.ts — the site's facts)
├─ fx/                 framework layer — portable to any project
│  ├─ components/      fully prop/slot-driven parts (no site content)
│  └─ lib/             pure functions
├─ styles/global.css   design system (token mapping + Tailwind recipes)
├─ themes/             design tokens — one CSS file per look + themes.ts registry
├─ routes.ts           central route manifest (URL → page module)
└─ icons/              custom SVG icons for astro-icon (Lucide comes from npm)
```

**Dependency rule: imports point downward only.**
Modules may use `shared`, `@fx`, `@data`, `@themes`, and design classes.
`fx/` may import **nothing** above it — no profile data, no nav, no theme files
(theme tokens reach it only as CSS variables at runtime).

Path aliases (tsconfig): `@modules/*`, `@fx/*`, `@data/*`, `@themes/*`, `@styles/*`.

## Naming

- `XxxPage.astro` — a page (registered in `src/routes.ts`).
- `XxxPart.astro` — a reusable component.
- `XxxLayout.astro` — a layout (`modules/shared/BaseLayout.astro`).
- A part used by one page lives in that page's module; used by several, in
  `modules/shared/`; usable by other projects, in `fx/components/`.

## Routing

There is no `src/pages/`. `src/routes.ts` maps every URL pattern to its page
module; the `central-routes` integration in `astro.config.mjs` injects them.
Adding a page = new module directory + one line in `routes.ts`.

## Styling ladder

1. **Tokens** (`src/themes/*.css`) — a theme is ~24 `--t-*` values; the token
   contract is documented in `themes/index.css`. `@theme inline` in
   `global.css` exposes them as utilities (`bg-bg`, `text-ink`, `text-accent`…).
   Never write a raw palette color (`slate-600`, `indigo-500`) in a component.
2. **Recipes** (`global.css` `@layer components`) — named classes for repeated
   patterns: `.title-*`, `.btn*`, `.card`, `.tag`, `.badge`, `.chip`,
   `.nav-pill`, `.menu-item`, `.icon-tile`, `.tip`, `.lede`, `.prose-article`…
   Extract a recipe only when a pattern repeats or has a clear name.
3. **Inline utilities** — everything else, directly in the markup.
4. **`style=` attribute** — only for data-driven values Tailwind cannot know
   (e.g. `SegmentBarPart` widths, theme swatches).
5. **`<style>` blocks in components — never.** The one non-Tailwind stylesheet
   is `modules/resume-print/resume-print.css` (the PDF is deliberately
   theme-independent print CSS).

## Articles

`modules/articles/registry.ts` lists metadata; each article is a directory
`modules/articles/content/<id>/` with `ArticlePart.astro` (plain HTML +
any local components/scripts/media). Listing, RSS, and routes read the registry.

## Themes

Adding a theme: create `src/themes/<name>.css` implementing the token
contract, import it in `themes/index.css`, add an entry in `themes.ts` —
it appears in the header dropdown automatically. Selection persists in
`localStorage` and is applied pre-paint in `BaseLayout`'s head script;
without a selection, dark is the default.
