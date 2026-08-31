import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://vasilegrafu.github.io',
  redirects: {
    '/resume': '/career',
  },
  integrations: [
    sitemap({
      filter: (page) => !page.includes('/resume-print/'),
    }),
  ],
  vite: {
    plugins: [tailwindcss()],
  },
});
