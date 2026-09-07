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
    <header className="border-line bg-bg/90 sticky top-0 z-10 border-b backdrop-blur">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-x-6 gap-y-2 px-4 py-3 sm:px-6 lg:px-8">
        <MenuButtonPart
          open={menuOpen}
          onToggle={() => setMenuOpen((o) => !o)}
          controls={MOBILE_MENU_ID}
        />
        <NavMenuPart />
        <div className="flex items-center gap-x-5">
          <SocialLinksPart />
          <ThemeMenuPart />
        </div>
      </div>
      <MobileMenuPart id={MOBILE_MENU_ID} open={menuOpen} onNavigate={() => setMenuOpen(false)} />
    </header>
  );
}
