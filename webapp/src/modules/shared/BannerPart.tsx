// Brand banner above the menu on every page: name and title over the theme's
// gradient, with two soft waves behind. The text is HTML, not SVG, so it wraps
// on narrow screens and scales with the type scale; only the waves are SVG,
// stretched to the banner's box so they follow every width.
import { site } from '@data/profile';

export default function BannerPart() {
  return (
    <div className="from-grad-a to-grad-b text-accent-ink relative overflow-hidden bg-gradient-to-r">
      <svg
        className="absolute inset-0 h-full w-full"
        viewBox="0 0 1200 250"
        preserveAspectRatio="none"
        aria-hidden="true"
      >
        <path d="M0 250C400 200 800 250 1200 150V250Z" fill="#fff" fillOpacity="0.14" />
        <path d="M0 250C600 280 900 100 1200 180V250Z" fill="#000" fillOpacity="0.16" />
      </svg>
      <div className="relative mx-auto max-w-7xl px-4 py-8 sm:px-6 sm:py-12 lg:px-8">
        <p className="title-hero text-accent-ink tracking-wide uppercase">{site.name}</p>
        <p className="text-accent-ink/85 mt-2 text-xl font-light text-balance">{site.title}</p>
      </div>
    </div>
  );
}
