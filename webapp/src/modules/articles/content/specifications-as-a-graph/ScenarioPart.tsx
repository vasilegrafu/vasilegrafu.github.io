// The story the whole article turns on, set apart from the prose and marked
// as what it is.
//
// It was two ordinary paragraphs, and it read as throat-clearing — the reader
// has no way to know yet that this is the example everything later is built
// on. The same thing in a panel, with the two moments dated, is read as a
// scenario: something being shown rather than something being said.
import type { ReactNode } from 'react';

interface Beat {
  /** What to call this moment, where it is worth naming. The opening beat
      needs nothing: it is the world before anything happens, and only what
      follows is measured against it. */
  when?: string;
  text: ReactNode;
}

export default function ScenarioPart({
  beats,
  children,
}: {
  beats: Beat[];
  children: ReactNode;
}) {
  return (
    <aside className="card bg-tint/40 my-8 p-5 sm:p-6">
      <p className="kicker">A scenario</p>
      <ol className="mt-4 list-none space-y-5 ps-0">
        {beats.map((b, i) => (
          <li key={i} className="border-accent-line border-s-2 ps-4">
            {b.when && <p className="title-card">{b.when}</p>}
            <p className={`text-muted ${b.when ? 'mt-1' : ''}`}>{b.text}</p>
          </li>
        ))}
      </ol>
      <p className="text-ink mt-5">{children}</p>
    </aside>
  );
}
