// Brand banner above the menu on every page: name and strapline over the theme's
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
      <div className="relative mx-auto max-w-7xl px-4 py-6 sm:px-6 sm:py-8 lg:px-8">
        {/* The strapline alone. The name is on the Career page, in
            the footer and on the resume; repeating it above every page was the
            loudest thing on the screen and said the least. Set at the size the
            name used to be, so the banner keeps its weight, but not in capitals
            — this is a sentence, not a wordmark. */}
        <p className="font-display text-3xl font-bold tracking-tight text-balance">
          {site.strapline}
        </p>
      </div>
    </div>
  );
}
