import { lazy, type ComponentType, type LazyExoticComponent } from 'react';
import { Link, useParams } from 'react-router';
import NotFoundPage from '@modules/404/NotFoundPage';
import PageMetaPart from '@modules/shared/PageMetaPart';
import { formatDate } from '@modules/articles/formatDate';
import { research } from './registry';

// Resolve each entry's content component by convention:
// content/<id>/ResearchPart.tsx — its own chunk, loaded when the entry opens.
// The glob matches nothing while there are no entries, which is fine.
const contentModules = import.meta.glob<{ default: ComponentType }>(
  './content/*/ResearchPart.tsx',
);
const contentById: Record<string, LazyExoticComponent<ComponentType>> = {};
for (const [path, load] of Object.entries(contentModules)) {
  const id = path.split('/')[2];
  contentById[id] = lazy(load);
}

export default function ResearchItemPage() {
  const { id = '' } = useParams();
  const entry = research.find((r) => r.id === id);
  const Content = contentById[id];
  if (!entry || !Content) return <NotFoundPage />;

  return (
    <>
      <PageMetaPart title={`${entry.title} — Vasile Grafu`} description={entry.description} />

      <article>
        <p className="text-faint">{formatDate(entry.pubDate)}</p>
        <h1 className="title-page mt-2">{entry.title}</h1>
        {entry.tags.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {entry.tags.map((t) => (
              <span key={t} className="tag">
                {t}
              </span>
            ))}
          </div>
        )}
        <div className="prose-article mt-8">
          <Content />
        </div>
      </article>
      <p className="mt-10">
        <Link to="/research" className="link-accent">
          ← All research
        </Link>
      </p>
    </>
  );
}
