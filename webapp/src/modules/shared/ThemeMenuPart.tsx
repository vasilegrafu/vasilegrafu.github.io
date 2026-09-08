// Theme dropdown: lists every registered theme (src/themes/themes.ts) and
// shows the active one on the button. Light is the default.
import { useEffect, useRef, useState } from 'react';
import IconPart from '@fx/components/IconPart';
import { cx } from '@fx/lib/cx';
import { themes } from '@themes/themes';
import { useTheme } from './useTheme';

export default function ThemeMenuPart() {
  const { theme, setTheme } = useTheme();
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onClick = (e: MouseEvent) => {
      if (!rootRef.current?.contains(e.target as Node)) setOpen(false);
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpen(false);
    };
    document.addEventListener('click', onClick);
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('click', onClick);
      document.removeEventListener('keydown', onKey);
    };
  }, [open]);

  const active = themes.find((t) => t.id === theme) ?? themes[0];

  return (
    <div className="relative" ref={rootRef}>
      <button
        type="button"
        aria-haspopup="menu"
        aria-expanded={open}
        data-tip="Change the site's color theme"
        onClick={() => setOpen((o) => !o)}
        className="tip tip-end border-line-strong text-muted hover:border-accent hover:text-accent inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 font-medium transition-colors"
      >
        <IconPart name="lucide:palette" className="h-4 w-4" />
        {/* The accessible name must contain the visible text, so the prefix
            is hidden rather than replacing the label. */}
        <span className="sr-only">Change theme, currently </span>
        <span>{active.label}</span>
        <IconPart
          name="lucide:chevron-down"
          className={cx('h-3.5 w-3.5 transition-transform', open && 'rotate-180')}
        />
      </button>

      {open && (
        <div role="menu" className="card bg-bg absolute top-full right-0 z-20 mt-2 w-44 p-1 shadow-lg">
          {themes.map((t) => {
            const isActive = t.id === theme;
            return (
              <button
                key={t.id}
                type="button"
                role="menuitemradio"
                aria-checked={isActive}
                onClick={() => {
                  setTheme(t.id);
                  setOpen(false);
                }}
                className="menu-item"
              >
                <span
                  className="border-line-strong h-3.5 w-3.5 rounded-full border"
                  style={{ background: t.swatch }}
                  aria-hidden="true"
                />
                <span className="grow text-start">{t.label}</span>
                {isActive && <IconPart name="lucide:check" className="text-accent h-4 w-4" />}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
