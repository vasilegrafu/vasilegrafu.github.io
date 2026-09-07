import { copyFileSync } from 'node:fs'
import { join } from 'node:path'
import { fileURLToPath, URL } from 'node:url'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig, type Plugin } from 'vite'
import { site } from './src/data/profile.ts'
import { articlesByDate } from './src/modules/articles/registry.ts'
import { routes } from './src/routes.ts'

const src = (dir: string) => fileURLToPath(new URL(`./src/${dir}`, import.meta.url))

const escapeXml = (s: string) =>
  s.replace(/[<>&'"]/g, (c) => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;', "'": '&apos;', '"': '&quot;' })[c]!)

/** Every indexable URL: static routes, with `/articles/:id` expanded from the registry. */
function sitemapUrls(): string[] {
  const urls: string[] = []
  for (const r of routes) {
    if (!r.sitemap) continue
    if (r.path === '/articles/:id') {
      for (const a of articlesByDate()) urls.push(`/articles/${a.id}`)
    } else {
      urls.push(r.path)
    }
  }
  return urls.map((p) => new URL(p, site.url).href)
}

function sitemapXml(): string {
  const entries = sitemapUrls().map((u) => `  <url><loc>${escapeXml(u)}</loc></url>`)
  return [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ...entries,
    '</urlset>',
    '',
  ].join('\n')
}

function rssXml(): string {
  const items = articlesByDate().map((a) => {
    const link = new URL(`/articles/${a.id}`, site.url).href
    return [
      '    <item>',
      `      <title>${escapeXml(a.title)}</title>`,
      `      <link>${escapeXml(link)}</link>`,
      `      <guid isPermaLink="true">${escapeXml(link)}</guid>`,
      `      <description>${escapeXml(a.description)}</description>`,
      `      <pubDate>${a.pubDate.toUTCString()}</pubDate>`,
      '    </item>',
    ].join('\n')
  })
  return [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
    '  <channel>',
    `    <title>${escapeXml(`${site.name} — Articles`)}</title>`,
    '    <description>Writing on engineering leadership, software architecture, and applied AI.</description>',
    `    <link>${escapeXml(site.url)}</link>`,
    `    <atom:link href="${escapeXml(new URL('/rss.xml', site.url).href)}" rel="self" type="application/rss+xml" />`,
    '    <language>en</language>',
    ...items,
    '  </channel>',
    '</rss>',
    '',
  ].join('\n')
}

// Static-site files a SPA on GitHub Pages still needs: sitemap.xml and rss.xml
// generated from the route manifest and article registry, and 404.html as a
// copy of index.html so deep links load the app and the router takes over.
function staticSiteFiles(): Plugin {
  return {
    name: 'static-site-files',
    apply: 'build',
    generateBundle() {
      this.emitFile({ type: 'asset', fileName: 'sitemap.xml', source: sitemapXml() })
      this.emitFile({ type: 'asset', fileName: 'rss.xml', source: rssXml() })
    },
    writeBundle(options) {
      const dir = options.dir ?? 'dist'
      copyFileSync(join(dir, 'index.html'), join(dir, '404.html'))
    },
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss(), staticSiteFiles()],
  resolve: {
    // Mirrors the "paths" in tsconfig.app.json.
    alias: {
      '@modules': src('modules'),
      '@fx': src('fx'),
      '@data': src('data'),
      '@themes': src('themes'),
      '@styles': src('styles'),
    },
  },
})
