// Article registry — the single list of all articles and their metadata.
// Each article lives in content/<id>/ArticlePart.tsx (plus any local
// components, scripts, or media its directory needs).
//
// This list is the only place an article has to be registered: routes.ts
// expands /articles/:id from it, the build prerenders one page per entry, and
// sitemap.xml and rss.xml are generated from it.
export interface ArticleMeta {
  id: string;
  title: string;
  description: string;
  pubDate: Date;
  tags: string[];
}

// Empty, for now: the one article, specifications-as-a-graph, moved to
// Research. Its old URL redirects there (`redirects` in routes.ts).
export const articles: ArticleMeta[] = [];

export const articlesByDate = () =>
  [...articles].sort((a, b) => b.pubDate.valueOf() - a.pubDate.valueOf());
