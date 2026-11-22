// Two pictures beside the contents list, as a way in.
//
// This article is long and its argument is made in pictures, but the first
// screen of it is prose: a date, a title, a contents list. A reader deciding
// whether to stay sees none of what the article actually has. These two say it
// in a glance — the graph laid out in layers, and one element of a live page
// with its requirement and rule beside it — and a press opens the whole tour.
//
// They sit side by side in the right half of the contents row, large enough
// that the shapes in them read at a glance: what the article covers on the
// left, what it looks like on the right.
import { useState } from 'react';
import ViewerPart from '@fx/components/ViewerPart';
import { plainClick } from '@fx/lib/plainClick';
import { asset } from './assets';
import { indexOfShot, PICS } from './shots';

/** Which of the tour's pictures to show here, and what each one promises. */
const TEASERS = [
  { name: 'layers.png', label: 'The whole specification, in layers' },
  { name: 'inspector.png', label: 'One element of a live page, inspected' },
];

/** The thumbnails are their own files, a quarter of the width of the originals
 *  and reduced to a 256-colour palette, which costs a screenshot of flat
 *  interface colours nothing visible. These two are the only pictures on the
 *  page that cannot be lazy-loaded — they are above the fold — so the pair is
 *  49 KB rather than the 1 MB the full-size ones weigh. */
const thumb = (name: string) => asset(`thumbs/${name}`);

export default function TeasersPart() {
  const [at, setAt] = useState<number | null>(null);
  return (
    <div className="flex w-full max-w-[40rem] shrink-0 gap-3 self-end md:w-[50%] md:gap-4 md:self-auto lg:w-[40rem]">
      {TEASERS.map((t) => (
        <a
          key={t.name}
          href={asset(t.name)}
          target="_blank"
          rel="noopener noreferrer"
          title={t.label}
          aria-label={`${t.label} — opens the tour of pictures`}
          onClick={plainClick(() => setAt(indexOfShot(t.name)))}
          className="card card-lift block min-w-0 flex-1 cursor-zoom-in overflow-hidden no-underline"
        >
          <img src={thumb(t.name)} alt="" width={640} height={400} className="block w-full" />
        </a>
      ))}
      {at !== null && <ViewerPart pics={PICS} start={at} onClose={() => setAt(null)} />}
    </div>
  );
}
