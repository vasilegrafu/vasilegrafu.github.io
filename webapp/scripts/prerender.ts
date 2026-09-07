// Post-build step (see "build" in package.json): renders every route to a
// static HTML file in dist/, so crawlers and social previews see real content
// and GitHub Pages answers deep links with a 200 instead of the 404 fallback.
// The client hydrates these pages (main.tsx); 404.html stays the empty shell.
//
// Each path is written twice — `career.html` and `career/index.html` — so
// both `/career` and `/career/` are served directly, without a redirect.
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { createServer } from 'vite';

const dist = join(import.meta.dirname, '..', 'dist');
const template = readFileSync(join(dist, 'index.html'), 'utf8');

/** Tags React hoists into <head>; they arrive at the start of the rendered output. */
const HOISTED = /^(?:<(?:title|meta|link)\b[^>]*>(?:[^<]*<\/title>)?)+/;

function injectIntoTemplate(rendered: string): string {
  const head = HOISTED.exec(rendered)?.[0] ?? '';
  const body = rendered.slice(head.length);
  return template
    .replace('</head>', `${head}\n  </head>`)
    .replace('<div id="root" class="flex min-h-screen flex-col"></div>', `<div id="root" class="flex min-h-screen flex-col">${body}</div>`);
}

function filesFor(path: string): string[] {
  if (path === '/') return [join(dist, 'index.html')];
  const rel = path.replace(/^\//, '');
  return [join(dist, `${rel}.html`), join(dist, rel, 'index.html')];
}

const vite = await createServer({
  server: { middlewareMode: true },
  appType: 'custom',
  logLevel: 'error',
});

try {
  const { render, prerenderPaths } = (await vite.ssrLoadModule('/src/prerender.tsx')) as {
    render: (path: string) => Promise<string>;
    prerenderPaths: () => string[];
  };
  for (const path of prerenderPaths()) {
    const page = injectIntoTemplate(await render(path));
    for (const file of filesFor(path)) {
      mkdirSync(dirname(file), { recursive: true });
      writeFileSync(file, page);
    }
    console.log(`prerendered ${path}`);
  }
} finally {
  await vite.close();
}
