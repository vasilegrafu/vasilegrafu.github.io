// Central route manifest — plain data, no React. routeTree.tsx turns it into
// route objects; the build reads it for sitemap.xml and prerendering. Adding a
// page = new module directory + one entry here + one lazy import in routeTree.tsx.
// (The import keeps its extension so vite.config.ts can load this file too.)
import { articlesByDate } from './modules/articles/registry.ts';

export type PageId =
  | 'index'
  | 'career'
  | 'skills'
  | 'projects'
  | 'articles'
  | 'article'
  | 'contact'
  | 'resume-print'
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
  { path: '/skills', page: 'skills', sitemap: true },
  { path: '/projects', page: 'projects', sitemap: true },
  { path: '/articles', page: 'articles', sitemap: true },
  { path: '/articles/:id', page: 'article', sitemap: true },
  { path: '/contact', page: 'contact', sitemap: true },
  { path: '/resume-print', page: 'resume-print', sitemap: false, bare: true },
  { path: '*', page: 'not-found', sitemap: false },
];

/** Old URLs that still get traffic. */
export const redirects: { from: string; to: string }[] = [
  { from: '/resume', to: '/career' },
  { from: '/ideas', to: '/' },
];

/** Concrete paths for a route: parameterised routes are expanded from their data. */
export function expandPath(path: string): string[] {
  if (path === '/articles/:id') return articlesByDate().map((a) => `/articles/${a.id}`);
  return [path];
}
