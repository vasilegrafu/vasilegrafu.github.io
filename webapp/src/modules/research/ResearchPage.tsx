import { Link } from 'react-router';
import PageMetaPart from '@modules/shared/PageMetaPart';
import { formatDate } from '@modules/articles/formatDate';
import type { ReactNode } from 'react';
import { researchByDate } from './registry';

const cardClass =
  'card card-lift group hover:border-accent flex flex-col gap-5 p-5 sm:flex-row sm:p-6';

/** The card's one link: out to `href` in a new tab when the entry lives elsewhere, else to its page here. */
function CardLink({ href, to, children }: { href?: string; to: string; children: ReactNode }) {
  return href ? (
    <a href={href} target="_blank" rel="noopener noreferrer" className={cardClass}>
      {children}
    </a>
  ) : (
    <Link to={to} className={cardClass}>
      {children}
    </Link>
  );
}

// The same shape as the Articles page: straight into the list, no heading or
// standfirst — the nav already says where you are.
//
// The list renders from `research` in registry.ts. While that is empty the
// page says so rather than showing an empty rule; sitemap.xml is generated
// from the same list, so it stays valid either way.
export default function ResearchPage() {
  const entries = researchByDate();
  return (
    <>
      <PageMetaPart
        title="Research — Vasile Grafu"
        description="Research notes and investigations on software architecture and applied AI."
      />

      {entries.length === 0 ? (
        <p className="text-muted pt-2 sm:pt-4">Nothing here yet. Research is on the way.</p>
      ) : (
        <ul className="space-y-6 pt-2 sm:pt-4">
          {entries.map((entry) => (
            // The whole entry is one card and one link, so it reads as
            // something to open rather than as a summary of the page itself:
            // the border and shadow lift on hover, and a "Read" line with an
            // arrow says where the click goes — the same cues as the link
            // cards on the Contact page.
            <li key={entry.id}>
              <CardLink href={entry.href} to={`/research/${entry.id}`}>
                {/* Above the text on a phone, beside it from sm up. 640×400, so
                    the box is reserved before the picture loads. */}
                {entry.thumbnail && (
                  <img
                    src={entry.thumbnail}
                    alt={entry.thumbnailAlt ?? ''}
                    width={640}
                    height={400}
                    className="border-line block h-auto w-full shrink-0 self-start rounded-lg border sm:w-64 lg:w-80"
                  />
                )}
                <div className="min-w-0">
                  <p className="text-faint">{formatDate(entry.pubDate)}</p>
                  <h2 className="title-item group-hover:text-accent mt-1 transition-colors">
                    {entry.title}
                  </h2>
                  {(entry.summary ?? [entry.description]).map((para) => (
                    <p key={para} className="text-muted mt-2">
                      {para}
                    </p>
                  ))}
                  {entry.tags.length > 0 && (
                    <div className="mt-4 flex flex-wrap gap-2">
                      {entry.tags.map((t) => (
                        <span key={t} className="tag">
                          {t}
                        </span>
                      ))}
                    </div>
                  )}
                  <p className="text-accent mt-4 inline-flex items-center gap-1.5 text-sm font-medium">
                    {entry.cta ?? 'Read the full piece'}
                    <span aria-hidden="true">{entry.href ? '↗' : '→'}</span>
                  </p>
                </div>
              </CardLink>
            </li>
          ))}
        </ul>
      )}
    </>
  );
}
