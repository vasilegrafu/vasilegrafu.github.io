import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import { site } from '../data/profile';

export async function GET(context) {
  const articles = await getCollection('articles');
  return rss({
    title: `${site.name} — Articles`,
    description: 'Writing on engineering leadership, software architecture, and applied AI.',
    site: context.site,
    items: articles.map((article) => ({
      title: article.data.title,
      description: article.data.description,
      pubDate: article.data.pubDate,
      link: `/articles/${article.id}/`,
    })),
  });
}
