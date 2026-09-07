// Generic routing helpers.

/** True when `path` is the given href or lives under it ('/' matches only itself). */
export const isActive = (href: string, path: string) =>
  href === '/' ? path === '/' : path.startsWith(href.replace(/\/$/, ''));
