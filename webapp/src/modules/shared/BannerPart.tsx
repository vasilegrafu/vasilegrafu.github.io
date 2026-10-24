// Brand banner above the menu on every page: a wall of terms from the work,
// set over the theme's gradient. The waves that used to sit behind it are gone
// — two textures in one strip argued with each other.
//
// The field is sliced centred, so the scale comes from the height and never
// the width: rows are never cropped top or bottom, and a wider window reveals
// more of the wall rather than stretching what is already there.
//
// The banner has two heights, so there are two scales: 1.0 below the sm
// breakpoint where it is 96px tall and the viewBox height matches exactly, and
// 1.167 above it where the banner grows to 112px. The type steps up with the
// banner, once, and holds steady either side of that.
//
// Both ends of the field fade out. The mask is in viewBox units rather than
// CSS, so it fades the field's own ends and not the banner's: on a window
// narrower than the field the fades sit off-screen and the wall simply fills
// the strip, and on one wider than it — an ultrawide — the wall dissolves into
// the gradient at both ends instead of stopping dead against a hard edge.
//
// The whole svg is aria-hidden. It is a texture, not a list of skills: those
// are on the Career page, where they can be read.
import { bannerWords, FIELD_WIDTH } from './bannerWords';

/** How much of each end dissolves, as a fraction of the field's width. */
const FADE = 0.05;

export default function BannerPart() {
  return (
    <div className="from-grad-a to-grad-b relative h-24 overflow-hidden bg-gradient-to-r sm:h-28">
      <svg
        className="font-sans absolute inset-0 h-full w-full"
        viewBox={`0 0 ${FIELD_WIDTH} 96`}
        preserveAspectRatio="xMidYMid slice"
        aria-hidden="true"
      >
        <defs>
          {/* In a mask, white keeps and black hides: opaque across the middle,
              falling away at each end. */}
          <linearGradient
            id="banner-fade"
            gradientUnits="userSpaceOnUse"
            x1="0"
            y1="0"
            x2={FIELD_WIDTH}
            y2="0"
          >
            <stop offset="0" stopColor="#000" />
            <stop offset={FADE} stopColor="#fff" />
            <stop offset={1 - FADE} stopColor="#fff" />
            <stop offset="1" stopColor="#000" />
          </linearGradient>
          <mask id="banner-mask">
            <rect x="0" y="0" width={FIELD_WIDTH} height="96" fill="url(#banner-fade)" />
          </mask>
        </defs>
        <g mask="url(#banner-mask)">
          {bannerWords.map((w, i) => (
            <text
              key={`${w.t}-${i}`}
              x={w.x}
              y={w.y}
              fontSize={w.s}
              fontWeight={w.w}
              fill={w.d ? '#000' : '#fff'}
              fillOpacity={w.o}
              xmlSpace="preserve"
            >
              {w.t}
            </text>
          ))}
        </g>
      </svg>
    </div>
  );
}
