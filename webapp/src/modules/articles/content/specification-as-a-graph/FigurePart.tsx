// One figure: a diagram or a screenshot, with its caption.
//
// The two want opposite treatment, and the file name says which is which. The
// diagrams are SVG with a transparent background and dark ink, so they need a
// light sheet under them or they vanish on a dark page; they get white, with a
// margin, like a drawing on paper, and the sheet is cut to the drawing rather
// than run to the full column. The screenshots are of an application in its
// own dark theme and carry their own background, so they get nothing but a
// border and fill it edge to edge.
//
// Neither runs the width of the page. The column here is wide enough for a
// screenshot to fill the screen on its own, and a picture that size stops
// being an illustration and becomes an interruption, so a screenshot is held
// to 56rem and centred. A diagram is held to its own size, which is narrower
// still.
//
// Either way the picture opens full size in a new tab, which is the only way
// to read the small print inside a screenshot, and the easiest way to study a
// diagram whose labels are deliberately smaller than the text around them.
import type { ReactNode } from 'react';
import { asset, diagramWidth, sizeOf } from './assets';

interface Props {
  /** File name inside the article's asset directory. .svg means a diagram. */
  name: string;
  alt: string;
  children: ReactNode;
}

export default function FigurePart({ name, alt, children }: Props) {
  const src = asset(name);
  const diagram = name.endsWith('.svg');
  const [w, h] = sizeOf(name);
  return (
    <figure className={`mx-auto my-8 ${diagram ? 'w-fit max-w-full' : 'max-w-4xl'}`}>
      <div
        className={`border-line overflow-hidden rounded-xl border ${diagram ? 'bg-white p-3' : ''}`}
      >
        <a href={src} target="_blank" rel="noopener noreferrer" className="block no-underline">
          <img
            src={src}
            alt={alt}
            width={w}
            height={h}
            loading="lazy"
            // A diagram is drawn to the width its labels ask for and only ever
            // shrinks from there; a screenshot fills the frame it was given.
            style={diagram ? { width: diagramWidth(name) } : undefined}
            className={diagram ? 'block h-auto max-w-full' : 'block w-full'}
          />
        </a>
      </div>
      <figcaption className="text-faint mt-3 text-xs">{children}</figcaption>
    </figure>
  );
}
