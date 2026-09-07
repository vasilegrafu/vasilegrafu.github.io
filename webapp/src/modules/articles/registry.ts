// Article registry — the single list of all articles and their metadata.
// Each article lives in content/<id>/ArticlePart.astro (plus any local
// components, scripts, or media its directory needs).
export interface ArticleMeta {
  id: string;
  title: string;
  description: string;
  pubDate: Date;
  tags: string[];
}

export const articles: ArticleMeta[] = [
  {
    id: 'why-i-built-this-site',
    title: 'Why I built this site',
    description:
      'A home for what I’ve learned in 20 years of software — engineering leadership, architecture, and the AI systems I’m building now.',
    pubDate: new Date('2026-08-31'),
    tags: ['meta'],
  },
];

export const articlesByDate = () =>
  [...articles].sort((a, b) => b.pubDate.valueOf() - a.pubDate.valueOf());
