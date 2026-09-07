// The theme choice: read from localStorage, written back on change, and
// applied as data-theme on <html>. The inline script in index.html applies the
// saved value before first paint; this hook takes over from there.
import { useCallback, useState } from 'react';

const STORAGE_KEY = 'theme';
const DEFAULT_THEME = 'light';

function readStored(): string {
  try {
    return localStorage.getItem(STORAGE_KEY) ?? DEFAULT_THEME;
  } catch {
    return DEFAULT_THEME;
  }
}

export function useTheme() {
  const [theme, setThemeState] = useState(readStored);

  const setTheme = useCallback((id: string) => {
    setThemeState(id);
    document.documentElement.setAttribute('data-theme', id);
    try {
      localStorage.setItem(STORAGE_KEY, id);
    } catch {
      // Private mode or storage disabled: the choice still applies for this visit.
    }
  }, []);

  return { theme, setTheme };
}
