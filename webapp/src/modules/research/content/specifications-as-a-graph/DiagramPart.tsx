// A diagram, drawn into the page rather than loaded as an image.
//
// Inlining is the point. These are line drawings on a transparent ground, and
// as an <img> they are a sealed document: the page's colours cannot reach
// inside, so on a dark theme the drawing has to sit on a white sheet of its
// own, which is a patch of daylight in the middle of a dark page. Drawn into
// the document, every colour in them is a --dg-* variable the theme sets, and
// the diagram is in the same ink as the text around it.
//
// The markup is read at build time, so it is in the prerendered HTML and
// identical after hydration. It comes from this directory, which is ours, and
// nothing in it is user input.
import { diagramWidth } from './assets';

const sources = import.meta.glob<string>('./diagrams/*.svg', {
  query: '?raw',
  import: 'default',
  eager: true,
});

interface Props {
  name: string;
  alt: string;
  /** Draw it to a smaller label size than the article's standard. */
  label?: number;
}

export default function DiagramPart({ name, alt, label }: Props) {
  const svg = sources[`./diagrams/${name}`];
  if (!svg) return null;
  return (
    <div
      className="diagram border-line mx-auto max-w-full overflow-hidden rounded-xl border p-3"
      style={{ width: diagramWidth(name, label) }}
      // One label for the whole drawing, so a reader hears what it shows
      // rather than every stray text node inside it.
      role="img"
      aria-label={alt}
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  );
}
