import { Link } from 'react-router';
import PageMetaPart from '@modules/shared/PageMetaPart';
import { formatDate } from './formatDate';
import { articlesByDate } from './registry';

export default function ArticlesPage() {
  const articles = articlesByDate();
  return (
    <>
      <PageMetaPart
        title="Articles — Vasile Grafu"
        description="Writing on engineering leadership, software architecture, and applied AI."
      />

      <p className="kicker">Writing</p>
      <h1 className="title-page mt-2">Articles</h1>
      <p className="lede">
        Writing on engineering leadership, software architecture, agentic AI systems, and
        AI-assisted development. Subscribe via{' '}
        <a href="/rss.xml" className="link-accent">
          RSS
        </a>
        .
      </p>

      <ul className="mt-8 space-y-8">
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
    </>
  );
}
