// Theme registry — the list the theme dropdown offers. Adding a theme means
// creating its .css file (see index.css for the token contract), importing it
// there, and adding an entry here.
export interface ThemeDef {
  id: string;
  label: string;
  /** Swatch color shown next to the theme name in the dropdown. */
  swatch: string;
}

export const themes: ThemeDef[] = [
  { id: 'light', label: 'Light', swatch: '#4f46e5' },
  { id: 'dark', label: 'Dark', swatch: '#020617' },
  { id: 'emerald', label: 'Emerald', swatch: '#047857' },
  { id: 'sepia', label: 'Sepia', swatch: '#9a3412' },
];
