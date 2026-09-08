// The site shell around every page: header, content, footer. Pages are lazy
// chunks, so the Outlet sits inside a Suspense boundary.
import { Suspense } from 'react';
import { Outlet, ScrollRestoration } from 'react-router';
import { themes } from '@themes/themes';
import FooterPart from './FooterPart';
import HeaderPart from './HeaderPart';
import { useTheme } from './useTheme';

const MAIN_ID = 'main';

export default function BaseLayout() {
  const { theme } = useTheme();
  const chrome = (themes.find((t) => t.id === theme) ?? themes[0]).chrome;

  return (
    <>
      {/* Mobile browser chrome follows the active theme's background. */}
      <meta name="theme-color" content={chrome} />
      <a href={`#${MAIN_ID}`} className="skip-link">
        Skip to content
      </a>
      <HeaderPart />
      <main id={MAIN_ID} className="mx-auto w-full max-w-7xl grow px-4 py-10 sm:px-6 lg:px-8">
        <Suspense>
          <Outlet />
        </Suspense>
      </main>
      <FooterPart />
      <ScrollRestoration />
    </>
  );
}
