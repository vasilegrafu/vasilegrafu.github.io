// Desktop pill navigation.
import { NavLink } from 'react-router';
import IconPart from '@fx/components/IconPart';
import { cx } from '@fx/lib/cx';
import { navItems } from './nav';

export default function NavMenuPart() {
  return (
    <nav className="hidden flex-wrap gap-1 text-sm sm:flex">
      {navItems.map((item) => (
        <NavLink
          key={item.href}
          to={item.href}
          end={item.href === '/'}
          className={({ isActive }) => cx('nav-pill', isActive && 'nav-pill-active')}
        >
          <IconPart name={item.icon} className="h-4 w-4" />
          {item.label}
        </NavLink>
      ))}
    </nav>
  );
}
