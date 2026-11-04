import { Link } from 'react-router';
import PageMetaPart from '@modules/shared/PageMetaPart';
import { formatDate } from './formatDate';
import { articlesByDate } from './registry';

// Straight into the list — no heading, no standfirst, the way the Now page
// opens straight into its first project. The nav already says where you are,
// and the feed is advertised to readers by the <link rel="alternate"> in
// index.html rather than by a line of prose here.
//
// The list renders from `articles` in registry.ts. While that is empty the
// page says so rather than showing an empty rule; rss.xml and sitemap.xml are
// generated from the same list, so both stay valid either way.
export default function ArticlesPage() {
  const articles = articlesByDate();
  return (
    <>
      <PageMetaPart
        title="Articles — Vasile Grafu"
        description="Writing on software architecture, applied AI, and engineering leadership."
      />

      {articles.length === 0 ? (
        <p className="text-muted pt-2 sm:pt-4">Nothing here yet. Articles are on the way.</p>
      ) : (
        <ul className="space-y-8 pt-2 sm:pt-4">
          {articles.map((article) => (
            <li key={article.id}>
              <Link to={`/articles/${article.id}`} className="group block">
                <p className="text-faint">{formatDate(article.pubDate)}</p>
                <h2 className="title-item group-hover:text-accent mt-1">{article.title}</h2>
                <p className="text-muted mt-2">{article.description}</p>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </>
  );
}
