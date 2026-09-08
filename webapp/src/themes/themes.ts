// Theme registry — the list the theme dropdown offers. Adding a theme means
// creating its .css file (see index.css for the token contract), importing it
// there, and adding an entry here.
export interface ThemeDef {
  id: string;
  label: string;
  /** Swatch color shown next to the theme name in the dropdown. */
  swatch: string;
  /** The theme's --t-bg, for the browser's theme-color (mobile address bar). */
  chrome: string;
}

export const themes: ThemeDef[] = [
  { id: 'light', label: 'Light', swatch: '#1e3a8a', chrome: '#ffffff' },
  { id: 'dark', label: 'Dark', swatch: '#0f172a', chrome: '#0b1120' },
  { id: 'emerald', label: 'Emerald', swatch: '#047857', chrome: '#f6faf8' },
  { id: 'sepia', label: 'Sepia', swatch: '#9a3412', chrome: '#f7f1e6' },
];
