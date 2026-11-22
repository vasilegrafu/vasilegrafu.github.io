// Central route manifest — plain data, no React. routeTree.tsx turns it into
// route objects; the build reads it for sitemap.xml and prerendering. Adding a
// page = new module directory + one entry here + one lazy import in routeTree.tsx.
// (The import keeps its extension so vite.config.ts can load this file too.)
import { articlesByDate } from './modules/articles/registry.ts';
import { researchByDate } from './modules/research/registry.ts';

export type PageId =
  | 'index'
  | 'career'
  | 'projects'
  | 'articles'
  | 'article'
  | 'research'
  | 'research-item'
  | 'contact'
  | 'resume-print'
  | 'version'
  | 'not-found';

export interface RouteDef {
  path: string;
  page: PageId;
  /** Listed in sitemap.xml (parameterised paths are expanded there). */
  sitemap: boolean;
  /** Rendered without the site shell (header/footer). */
  bare?: boolean;
}

export const routes: RouteDef[] = [
  { path: '/', page: 'index', sitemap: true },
  { path: '/career', page: 'career', sitemap: true },
  { path: '/projects', page: 'projects', sitemap: true },
  { path: '/articles', page: 'articles', sitemap: true },
  { path: '/articles/:id', page: 'article', sitemap: true },
  { path: '/research', page: 'research', sitemap: true },
  { path: '/research/:id', page: 'research-item', sitemap: true },
  { path: '/contact', page: 'contact', sitemap: true },
  { path: '/resume-print', page: 'resume-print', sitemap: false, bare: true },
  { path: '/version', page: 'version', sitemap: false },
  { path: '*', page: 'not-found', sitemap: false },
];

/**
 * URLs that moved, kept working because they were published elsewhere — the
 * LinkedIn edition of "Specifications as a graph" links to its /articles URL.
 * GitHub Pages cannot send a real redirect, so the build writes a small page
 * at each `from` that forwards to `to` (vite.config.ts); an immediate meta
 * refresh plus a canonical link is what search engines read as a move.
 */
export const redirects: { from: string; to: string }[] = [
  { from: '/articles/specifications-as-a-graph', to: '/research/specifications-as-a-graph' },
];

/** Concrete paths for a route: parameterised routes are expanded from their data. */
export function expandPath(path: string): string[] {
  if (path === '/articles/:id') return articlesByDate().map((a) => `/articles/${a.id}`);
  if (path === '/research/:id')
    return researchByDate()
      .filter((r) => !r.href) // links out: no page of its own
      .map((r) => `/research/${r.id}`);
  return [path];
}
