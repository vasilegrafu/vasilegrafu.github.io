import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import sitemap from '@astrojs/sitemap';
import icon from 'astro-icon';
import { routes } from './src/routes';

// Registers every route from the central manifest (src/routes.ts),
// replacing Astro's file-based src/pages routing.
const centralRoutes = () => ({
  name: 'central-routes',
  hooks: {
    'astro:config:setup': ({ injectRoute }) => {
      for (const route of routes) injectRoute(route);
    },
  },
});

export default defineConfig({
  site: 'https://vasilegrafu.github.io',
  redirects: {
    '/resume': '/career',
    '/ideas': '/',
  },
  integrations: [
    centralRoutes(),
    icon(),
    sitemap({
      filter: (page) => !page.includes('/resume-print/'),
    }),
  ],
  vite: {
    plugins: [tailwindcss()],
  },
});
