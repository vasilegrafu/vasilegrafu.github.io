// Phone-only page pager, under the menu row: walk the site in nav order with
// one tap instead of opening the dropdown every time. The dots say how many
// pages there are and which one this is — something the arrows alone cannot.
//
// Deliberately not styled like the menu above it: its own ground, a hairline
// between the two, and controls spread edge to edge rather than a row of tabs.
//
// Pages outside the nav list (an article, /version, the 404) have no position
// in the sequence, so nothing renders. The ends stop rather than wrap: on the
// first and last page the arrow stays but goes quiet, so the row never jumps.
import { Link, useLocation } from 'react-router';
import IconPart from '@fx/components/IconPart';
import { cx } from '@fx/lib/cx';
import { navItems } from './nav';

export default function PagerPart() {
  const { pathname } = useLocation();
  // startsWith, so an article page still anchors to Articles — navigation that
  // disappears on a sub-page is worse than navigation positioned loosely.
  const index = navItems.findIndex((item) =>
    item.href === '/' ? pathname === '/' : pathname.startsWith(item.href),
  );
  if (index === -1) return null;

  const prev = index > 0 ? navItems[index - 1] : undefined;
  const next = index < navItems.length - 1 ? navItems[index + 1] : undefined;

  return (
    <nav aria-label="Page pager" className="border-line bg-surface border-t sm:hidden">
      <div className="mx-auto flex max-w-7xl items-center gap-3 px-2">
        {prev ? (
          <Link to={prev.href} aria-label={`Previous page: ${prev.label}`} className="pager-link">
            <IconPart name="lucide:chevron-left" className="h-4 w-4 shrink-0" />
            <span className="truncate">{prev.label}</span>
          </Link>
        ) : (
          <span className="pager-link pager-link-off" aria-hidden="true">
            <IconPart name="lucide:chevron-left" className="h-4 w-4 shrink-0" />
          </span>
        )}

        {/* One dot per nav page: position in the sequence, which the arrows
            cannot show on their own. */}
        <span className="flex shrink-0 items-center gap-1.5" aria-hidden="true">
          {navItems.map((item, i) => (
            <span
              key={item.href}
              className={cx(
                'h-1.5 w-1.5 rounded-full',
                i === index ? 'bg-accent' : 'bg-line-strong',
              )}
            />
          ))}
        </span>

        {next ? (
          <Link
            to={next.href}
            aria-label={`Next page: ${next.label}`}
            className="pager-link justify-end"
          >
            <span className="truncate">{next.label}</span>
            <IconPart name="lucide:chevron-right" className="h-4 w-4 shrink-0" />
          </Link>
        ) : (
          <span className="pager-link pager-link-off justify-end" aria-hidden="true">
            <IconPart name="lucide:chevron-right" className="h-4 w-4 shrink-0" />
          </span>
        )}
      </div>
    </nav>
  );
}
