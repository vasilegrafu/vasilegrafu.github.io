import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import sitemap from '@astrojs/sitemap';
import icon from 'astro-icon';

export default defineConfig({
  site: 'https://vasilegrafu.github.io',
  redirects: {
    '/resume': '/career',
    '/ideas': '/',
  },
  integrations: [
    icon(),
    sitemap({
      filter: (page) => !page.includes('/resume-print/'),
    }),
  ],
  vite: {
    plugins: [tailwindcss()],
  },
});
