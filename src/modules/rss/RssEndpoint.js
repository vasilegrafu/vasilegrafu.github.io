import rss from '@astrojs/rss';
import { site } from '../../data/profile';
import { articlesByDate } from '../articles/registry';

export async function GET(context) {
  return rss({
    title: `${site.name} — Articles`,
    description: 'Writing on engineering leadership, software architecture, and applied AI.',
    site: context.site,
    items: articlesByDate().map((article) => ({
      title: article.title,
      description: article.description,
      pubDate: article.pubDate,
      link: `/articles/${article.id}/`,
    })),
  });
}
