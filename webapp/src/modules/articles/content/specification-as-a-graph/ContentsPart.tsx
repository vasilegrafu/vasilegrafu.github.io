// What is in the article, before the article starts.
//
// It is a long read with a tour of fifteen screens in the middle of it, and
// the people it is written for arrive wanting different parts: a manager
// wants the comparison, a developer wants how it works, most people want the
// pictures. Numbered, because the order is the argument — the problem, then
// the answer, then the proof — and a reader who skips straight to the middle
// should be able to see what they are skipping.
//
// Plain anchors, so they work in the prerendered page before any JavaScript
// has loaded, and so each one can be copied and sent to someone.
//
// Once the app is running they need help, though. The shell renders react
// router's ScrollRestoration, which treats the hash change as a navigation
// and puts the page back where it was — which is the top. So a plain click
// does the scroll itself and only then writes the hash, with replaceState so
// eleven glances at the contents do not become eleven entries in the back
// button. Anything the browser should own — a middle click, a modified click,
// an unknown id — falls through to the anchor untouched.
import type { MouseEvent } from 'react';
import { SECTIONS, slug } from './sections';

export default function ContentsPart() {
  const titles = Object.values(SECTIONS);

  const jump = (e: MouseEvent<HTMLAnchorElement>, id: string) => {
    if (e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    const target = document.getElementById(id);
    if (!target) return;
    e.preventDefault();
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    history.replaceState(null, '', `#${id}`);
  };
  return (
    <nav aria-label="Sections of this article" className="card bg-tint/40 my-8 p-5">
      <p className="kicker">Contents</p>
      {/* Two columns read down, not across: six rows, then the flow turns the
          corner. Numbered in one sequence either way, but a contents list is
          scanned top to bottom. */}
      <ol className="mt-3 grid list-none grid-cols-1 gap-x-8 gap-y-2 ps-0 sm:grid-flow-col sm:grid-cols-2 sm:grid-rows-6">
        {titles.map((t, i) => (
          <li key={t} className="flex gap-2.5">
            <span className="text-faint font-display text-xs tabular-nums">
              {String(i + 1).padStart(2, '0')}
            </span>
            <a
              href={`#${slug(t)}`}
              onClick={(e) => jump(e, slug(t))}
              className="text-muted hover:text-accent text-xs no-underline"
            >
              {t}
            </a>
          </li>
        ))}
      </ol>
    </nav>
  );
}
