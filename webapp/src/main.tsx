import { StrictMode } from 'react';
import { createRoot, hydrateRoot } from 'react-dom/client';
import { RouterProvider } from 'react-router/dom';
import '@fontsource-variable/inter';
import '@fontsource-variable/space-grotesk';
import '@styles/global.css';
import { router } from './router';

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
