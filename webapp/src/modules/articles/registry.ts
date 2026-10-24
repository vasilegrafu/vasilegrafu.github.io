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

// Deliberately empty, for now. The article that was here still lives under
// content/why-i-built-this-site/, so putting its entry back is all it takes to
// publish it again. While this list is empty the listing page shows a
// placeholder, /articles/:id prerenders nothing and returns the 404 page, and
// rss.xml and sitemap.xml are generated with no items but stay valid.
export const articles: ArticleMeta[] = [];

export const articlesByDate = () =>
  [...articles].sort((a, b) => b.pubDate.valueOf() - a.pubDate.valueOf());
