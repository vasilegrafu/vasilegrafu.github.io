import { lazy, type ComponentType, type LazyExoticComponent } from 'react';
import { Link, useParams } from 'react-router';
import NotFoundPage from '@modules/404/NotFoundPage';
import PageMetaPart from '@modules/shared/PageMetaPart';
import { formatDate } from './formatDate';
import { articles } from './registry';

// Resolve each article's content component by convention:
// content/<id>/ArticlePart.tsx — its own chunk, loaded when the article opens.
const contentModules = import.meta.glob<{ default: ComponentType }>(
  './content/*/ArticlePart.tsx',
);
const contentById: Record<string, LazyExoticComponent<ComponentType>> = {};
for (const [path, load] of Object.entries(contentModules)) {
  const id = path.split('/')[2];
  contentById[id] = lazy(load);
}

export default function ArticlePage() {
  const { id = '' } = useParams();
  const article = articles.find((a) => a.id === id);
  const Content = contentById[id];
  if (!article || !Content) return <NotFoundPage />;

  return (
    <>
      <PageMetaPart title={`${article.title} — Vasile Grafu`} description={article.description} />

      <article>
        <p className="text-faint">{formatDate(article.pubDate)}</p>
        <h1 className="title-page mt-2">{article.title}</h1>
        {article.tags.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {article.tags.map((t) => (
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
        <Link to="/articles" className="link-accent">
          ← All articles
        </Link>
      </p>
    </>
  );
}
