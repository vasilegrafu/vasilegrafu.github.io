// Dropdown nav panel shown below the header on mobile; opened by MenuButtonPart.
import { NavLink } from 'react-router';
import IconPart from '@fx/components/IconPart';
import { cx } from '@fx/lib/cx';
import { navItems } from './nav';

interface Props {
  id: string;
  open: boolean;
  /** Called when a link is chosen, so the parent can close the panel. */
  onNavigate: () => void;
}

export default function MobileMenuPart({ id, open, onNavigate }: Props) {
  if (!open) return null;
  return (
    <div id={id} className="border-line border-t sm:hidden">
      <nav className="mx-auto flex max-w-7xl flex-col gap-1 px-4 py-3 text-sm sm:px-6 lg:px-8">
        {navItems.map((item) => (
          <NavLink
            key={item.href}
            to={item.href}
            end={item.href === '/'}
            onClick={onNavigate}
            className={({ isActive }) => cx('menu-item', isActive && 'menu-item-active')}
          >
            <IconPart name={item.icon} className="h-4.5 w-4.5" />
            {item.label}
          </NavLink>
        ))}
      </nav>
    </div>
  );
}
