import { StrictMode } from 'react';
import { createRoot, hydrateRoot } from 'react-dom/client';
import { RouterProvider } from 'react-router/dom';
import '@fontsource-variable/inter';
import '@fontsource-variable/space-grotesk';
import '@styles/global.css';
import { router } from './router';

// After a deploy, a page opened before it still references the previous
// build's chunk hashes, so the next lazy navigation fails to fetch. Reload
// once to pick up the new build; the flag stops a loop if it is still missing.
window.addEventListener('vite:preloadError', () => {
  const key = `reloaded:${window.location.pathname}`;
  try {
    if (sessionStorage.getItem(key)) return;
    sessionStorage.setItem(key, '1');
  } catch {
    // Storage unavailable: reload anyway, once is better than a broken page.
  }
  window.location.reload();
});

const container = document.getElementById('root')!;
const app = (
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>
);

// Pages are prerendered at build time (scripts/prerender.ts) and hydrate here.
// The 404.html fallback ships an empty root and renders from scratch.
if (container.hasChildNodes()) {
  hydrateRoot(container, app);
} else {
  createRoot(container).render(app);
}
