// The tour of the application: twelve screens, three to a row.
//
// They are thumbnails on purpose. At any size an article column allows, the
// text inside one of these screenshots is too small to read and only the shape
// comes through — so the tile shows the shape, the caption says what to look
// for, and a click opens the picture full screen, where it can be zoomed into
// and dragged around, and walked to the next one. A modified or middle click
// still opens the file itself in a tab — see plainClick.
//
// One piece of state for the whole grid rather than one per tile: there is only
// ever one picture open, and holding it here keeps each tile a plain figure.
import { useState } from 'react';
import ViewerPart from '@fx/components/ViewerPart';
import { plainClick } from '@fx/lib/plainClick';
import { asset, SHOT } from './assets';
import { PICS } from './shots';

export interface Shot {
  name: string;
  kicker: string;
  title: string;
  alt: string;
  caption: string;
}

export default function GalleryPart({ shots }: { shots: Shot[] }) {
  const [at, setAt] = useState<number | null>(null);
  return (
    <div className="my-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
      {shots.map((s, i) => (
        <figure key={s.name}>
          <a
            href={asset(s.name)}
            target="_blank"
            rel="noopener noreferrer"
            onClick={plainClick(() => setAt(i))}
            className="card card-lift block cursor-zoom-in overflow-hidden no-underline"
          >
            <img
              src={asset(s.name)}
              alt={s.alt}
              width={SHOT[0]}
              height={SHOT[1]}
              loading="lazy"
              className="block w-full"
            />
          </a>
          <figcaption className="mt-3">
            <p className="kicker">{s.kicker}</p>
            <p className="title-card mt-1">{s.title}</p>
            <p className="text-faint mt-1 text-xs">{s.caption}</p>
          </figcaption>
        </figure>
      ))}
      {at !== null && <ViewerPart pics={PICS} start={at} onClose={() => setAt(null)} />}
    </div>
  );
}
