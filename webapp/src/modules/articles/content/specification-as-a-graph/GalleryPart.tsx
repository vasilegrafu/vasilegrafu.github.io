// The tour of the application: twelve screens, three to a row.
//
// They are thumbnails on purpose. At any size an article column allows, the
// text inside one of these screenshots is too small to read and only the shape
// comes through — so the tile shows the shape, the caption says what to look
// for, and a click opens the full picture in its own tab.
import { asset, SHOT } from './assets';

export interface Shot {
  name: string;
  kicker: string;
  title: string;
  alt: string;
  caption: string;
}

export default function GalleryPart({ shots }: { shots: Shot[] }) {
  return (
    <div className="my-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
      {shots.map((s) => (
        <figure key={s.name}>
          <a
            href={asset(s.name)}
            target="_blank"
            rel="noopener noreferrer"
            className="card card-lift block overflow-hidden no-underline"
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
    </div>
  );
}
