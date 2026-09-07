/** Joins class names, dropping falsy entries — the React stand-in for Astro's class:list. */
export const cx = (...parts: Array<string | false | null | undefined>) =>
  parts.filter(Boolean).join(' ');
