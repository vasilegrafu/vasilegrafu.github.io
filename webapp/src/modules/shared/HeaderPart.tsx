// Sticky site header: nav pills (desktop) / hamburger (mobile) on the left,
// social links and theme toggle on the right, mobile dropdown panel below.
import { useState } from 'react';
import MenuButtonPart from '@fx/components/MenuButtonPart';
import MobileMenuPart from './MobileMenuPart';
import NavMenuPart from './NavMenuPart';
import SocialLinksPart from './SocialLinksPart';
import ThemeMenuPart from './ThemeMenuPart';

const MOBILE_MENU_ID = 'mobile-menu';

export default function HeaderPart() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="bg-bar/95 border-line-strong sticky top-0 z-10 border-b shadow-sm backdrop-blur">
      {/* Brand stripe along the top edge; the strong border closes the bar
          at the bottom, so the menu reads as its own band. */}
      <div className="from-grad-a to-grad-b h-[3px] bg-gradient-to-r" aria-hidden="true" />
      {/* No vertical padding here: the nav tabs carry their own so their
          active rule sits on the bar's bottom edge; the other controls pad
          themselves to the same height. */}
      <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-x-6 px-4 sm:px-6 lg:px-8">
        <div className="py-3 sm:hidden">
          <MenuButtonPart
            open={menuOpen}
            onToggle={() => setMenuOpen((o) => !o)}
            controls={MOBILE_MENU_ID}
          />
        </div>
        <NavMenuPart />
        <div className="flex items-center gap-x-5 py-3">
          <SocialLinksPart />
          <ThemeMenuPart />
        </div>
      </div>
      <MobileMenuPart id={MOBILE_MENU_ID} open={menuOpen} onNavigate={() => setMenuOpen(false)} />
    </header>
  );
}
