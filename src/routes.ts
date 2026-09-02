// Central route manifest — the single place where URLs map to page modules.
// Consumed by the `central-routes` integration in astro.config.mjs.
export interface RouteDef {
  pattern: string;
  entrypoint: string;
}

export const routes: RouteDef[] = [
  { pattern: '/', entrypoint: './src/modules/index/IndexPage.astro' },
  { pattern: '/career', entrypoint: './src/modules/career/CareerPage.astro' },
  { pattern: '/projects', entrypoint: './src/modules/projects/ProjectsPage.astro' },
  { pattern: '/articles', entrypoint: './src/modules/articles/ArticlesPage.astro' },
  { pattern: '/articles/[id]', entrypoint: './src/modules/articles/ArticlePage.astro' },
  { pattern: '/contact', entrypoint: './src/modules/contact/ContactPage.astro' },
  { pattern: '/resume-print', entrypoint: './src/modules/resume-print/ResumePrintPage.astro' },
  { pattern: '/404', entrypoint: './src/modules/404/NotFoundPage.astro' },
  { pattern: '/rss.xml', entrypoint: './src/modules/rss/RssEndpoint.js' },
];
