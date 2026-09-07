# Discoverability: SEO, feeds and social previews

How the site is made visible to search engines, feed readers and link
previews, and what to keep in mind when adding a page or an article. Paths are
relative to `webapp/`.

## The problem a single-page app has

A React SPA ships one `index.html` with an empty `<div id="root">` and builds
the page in the browser. Crawlers and link-preview bots that do not run
JavaScript see nothing, and on GitHub Pages every deep link like `/career` is
answered by `404.html` with a 404 status. Everything below exists to close
that gap.

## 1. Prerendered HTML for every page

`scripts/prerender.ts` runs as the last step of `npm run build`. It loads the
app in Node through Vite, renders each route with React's static prerender API
and React Router's static handler, and writes the result into `dist/` as real
HTML — the full page markup inside `#root`, and the page's head tags in
`<head>`.

- Which paths: every entry in `src/routes.ts` except `*`, with `/articles/:id`
  expanded from the article registry (`src/prerender.tsx`, `prerenderPaths`).
- File layout: each path is written twice, `career.html` and
  `career/index.html`, so GitHub Pages serves both `/career` and `/career/`
  directly with a 200 and no redirect. The home page overwrites `index.html`.
- In the browser, `src/main.tsx` hydrates the prerendered markup instead of
  rendering from scratch, so there is no flash and no duplicate work.
- `404.html` stays the empty shell. It is what GitHub Pages serves for unknown
  URLs and for the redirect routes (`/resume`, `/ideas`); the client renders
  the 404 page or the redirect there.

Hydration rule: the first client render must match the server output. State
that differs per visitor (the saved theme) goes through `useSyncExternalStore`
with a server snapshot (`useTheme.ts`), so the page hydrates as rendered and
then updates. Anything else that reads `localStorage`, `window` size or the
clock at render time needs the same treatment.

## 2. Per-page head metadata

`src/modules/shared/PageMetaPart.tsx` renders, for every page:

- `<title>` and `<meta name="description">`
- `<link rel="canonical">` and `og:url` — always the no-trailing-slash form
  (`https://vasilegrafu.github.io/career`), whichever way the page was reached
- `og:title` and `og:description`
- `<meta name="robots" content="noindex">` when `noindex` is set (the resume
  print page, the 404 page)

React 19 hoists these into `<head>`; at build time the prerenderer moves them
into the static `<head>` of the HTML file, so they are there before any script
runs. Site-wide tags that never change per page live in `index.html`:
`og:type`, `og:site_name`, the Open Graph / Twitter image, `theme-color`, the
favicon, and the RSS `<link rel="alternate">`.

Every page component must render one `PageMetaPart` with a specific title and
description — the description is what appears under the link in search
results and in previews.

## 3. URLs

- One canonical form per page: no trailing slash. Internal links, the sitemap,
  the feed and the canonical tag all use it. Both forms are served (see the
  file layout above), so old links keep working.
- Old URLs that still get traffic are listed in `redirects` in
  `src/routes.ts` and become client-side redirects. They are not in the
  sitemap.
- Article slugs are the directory names under `src/modules/articles/content/`
  and the `id` in the registry. Once published, a slug is a URL — do not rename.

## 4. Sitemap and robots

The `static-site-files` plugin in `vite.config.ts` writes `dist/sitemap.xml`
at build time: every route flagged `sitemap: true` in `src/routes.ts`, with
article routes expanded from the registry. `public/robots.txt` allows
everything and points at the sitemap. The resume print page is not in the
sitemap and carries `noindex`.

To get indexed faster, submit `https://vasilegrafu.github.io/sitemap.xml` in
Google Search Console (a one-time, manual step — the site has no tracking or
verification tag; Search Console can verify ownership through the GitHub
Pages DNS/HTML-file methods).

## 5. RSS feed

The same plugin writes `dist/rss.xml` from the article registry: title,
description, link and publication date per article, newest first. The feed is
advertised in `index.html` via `<link rel="alternate" type="application/rss+xml">`
and linked from the Articles page and the footer. Adding an article to the
registry is all it takes to publish it in the feed.

## 6. Social previews

Link previews on LinkedIn, Slack, X and the like read the Open Graph tags.
The image is `public/og.png` (1200×630), generated from `design/og-image.html`
— open that file in a browser at 1200×630 and screenshot it to regenerate.
Title and description come from `PageMetaPart`, so every page previews with
its own text.

## 7. The resume PDF

`public/cv.pdf` is linked from the Career page and is a plain static file, so
it is crawlable and downloadable without JavaScript. It is printed from the
`/resume-print` route; the README has the command.

## Checklist when adding a page

1. Module directory + entry in `src/routes.ts` + lazy import in
   `src/routeTree.tsx`.
2. The page renders `PageMetaPart` with a specific title and description.
3. `sitemap: true` unless the page should stay out of search; add `noindex`
   for pages that must not be indexed.
4. Build and check `dist/<path>.html` exists and contains the content and the
   right `<title>`.

Adding an article needs only the registry entry and the content directory;
prerendering, sitemap and RSS follow from the registry.

## How to verify after a deploy

```sh
curl -sI https://vasilegrafu.github.io/career | head -1      # HTTP/2 200
curl -s  https://vasilegrafu.github.io/career | grep -o '<title>[^<]*'
curl -s  https://vasilegrafu.github.io/sitemap.xml
curl -s  https://vasilegrafu.github.io/rss.xml
```

For previews, paste a page URL into LinkedIn's Post Inspector or
opengraph.xyz; for search, Google's Rich Results Test shows the page as
Googlebot renders it.
