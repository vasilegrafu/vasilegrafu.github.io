// Build-time rendering of one route to HTML. Loaded by scripts/prerender.ts
// through Vite's SSR module loader, so aliases, CSS imports and lazy pages all
// resolve the same way they do in the browser build.
import { StrictMode } from 'react';
import { prerender } from 'react-dom/static';
import { createStaticHandler, createStaticRouter, StaticRouterProvider } from 'react-router';
import { site } from '@data/profile';
import { routeObjects } from './routeTree';
import { expandPath, routes } from './routes';

/** Every path that gets its own prerendered HTML file: all real pages, expanded. */
export const prerenderPaths = (): string[] =>
  routes.filter((r) => r.path !== '*').flatMap((r) => expandPath(r.path));

/** Renders the app at `path` and resolves once every lazy page chunk has loaded. */
export async function render(path: string): Promise<string> {
  const handler = createStaticHandler(routeObjects);
  const context = await handler.query(new Request(new URL(path, site.url)));
  if (context instanceof Response) {
    throw new Error(`Unexpected ${context.status} response while prerendering ${path}`);
  }
  const router = createStaticRouter(handler.dataRoutes, context);
  const { prelude } = await prerender(
    <StrictMode>
      <StaticRouterProvider router={router} context={context} />
    </StrictMode>,
  );
  return new Response(prelude).text();
}
