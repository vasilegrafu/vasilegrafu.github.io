// Brand banner above the menu on every page: a wall of terms from my own work,
// set over the theme's gradient. The waves that used to sit behind it are gone
// — two textures in one strip argued with each other.
//
// `slice`, not `none`: stretching the viewBox to the banner's shape would
// squash the letterforms, badly so on a phone. Slicing scales it evenly and
// crops instead, so the type keeps its proportions at every width.
//
// The whole thing is aria-hidden. It is a texture, not a list of skills: those
// are on the Career page, where they can be read.
import { bannerWords } from './bannerWords';

export default function BannerPart() {
  return (
    <div className="from-grad-a to-grad-b relative h-24 overflow-hidden bg-gradient-to-r sm:h-28">
      <svg
        className="font-sans absolute inset-0 h-full w-full"
        viewBox="0 0 1200 96"
        preserveAspectRatio="xMidYMid slice"
        aria-hidden="true"
      >
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
      </svg>
    </div>
  );
}
