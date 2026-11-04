// A section heading, with the anchor the contents list points at.
//
// The id is derived from the title rather than written beside it, so the two
// cannot disagree. scroll-mt keeps the heading clear of the sticky header
// when you arrive by link — without it the browser scrolls the heading to the
// very top, where the bar is already sitting.
import { slug } from './sections';

export default function SectionPart({ title }: { title: string }) {
  return (
    <h2 id={slug(title)} className="scroll-mt-20">
      {title}
    </h2>
  );
}
