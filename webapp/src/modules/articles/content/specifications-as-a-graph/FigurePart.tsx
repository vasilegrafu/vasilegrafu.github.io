// One figure: a diagram or a screenshot, with its caption.
//
// The two are different things and the file name says which is which. A
// diagram is a line drawing in the theme's own colours, drawn into the page
// by DiagramPart. A screenshot is a photograph of an application in its own
// dark theme: it carries its background with it, so it gets a border and
// nothing else, and a click opens it full screen in ViewerPart, which is the
// only way to read the small print inside one. A modified or middle click
// still opens the file itself in a tab — see plainClick.
//
// Neither runs the width of the page. The column here is wide enough for a
// screenshot to fill the screen on its own, and a picture that size stops
// being an illustration and becomes an interruption, so a screenshot is held
// to 56rem and centred. A diagram is held to its own width, which is narrower
// still — see assets.ts for what sets it.
import { useState } from 'react';
import type { ReactNode } from 'react';
import ViewerPart from '@fx/components/ViewerPart';
import { plainClick } from '@fx/lib/plainClick';
import { asset, sizeOf } from './assets';
import DiagramPart from './DiagramPart';

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
  const [open, setOpen] = useState(false);
  return (
    <figure className={`mx-auto my-8 ${diagram ? 'w-fit max-w-full' : 'max-w-4xl'}`}>
      {diagram ? (
        <DiagramPart name={name} alt={alt} />
      ) : (
        <div className="border-line overflow-hidden rounded-xl border">
          <a
            href={src}
            target="_blank"
            rel="noopener noreferrer"
            onClick={plainClick(() => setOpen(true))}
            className="block cursor-zoom-in no-underline"
          >
            <img
              src={src}
              alt={alt}
              width={w}
              height={h}
              loading="lazy"
              className="block w-full"
            />
          </a>
        </div>
      )}
      <figcaption className="text-faint mt-3 text-xs">{children}</figcaption>
      {open && <ViewerPart pics={[{ src, alt }]} onClose={() => setOpen(false)} />}
    </figure>
  );
}
