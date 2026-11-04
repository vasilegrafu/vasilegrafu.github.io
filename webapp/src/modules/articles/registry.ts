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

export const articles: ArticleMeta[] = [
  {
    id: 'specification-as-a-graph',
    title: 'Specification as a graph',
    description:
      'A product specification held as a graph of small, linked facts: an AI assistant writes it with you, people read it in a browser, agents build from it, and every change shows what it touches before it is made.',
    pubDate: new Date('2026-11-04'),
    tags: ['AI-assisted development', 'Product specification', 'Agentic architectures'],
  },
];

export const articlesByDate = () =>
  [...articles].sort((a, b) => b.pubDate.valueOf() - a.pubDate.valueOf());
