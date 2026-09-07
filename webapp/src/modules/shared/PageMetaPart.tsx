// Per-page document metadata. React 19 hoists <title>, <meta> and <link>
// rendered anywhere in the tree into <head>, so every page renders one of
// these; the site-wide, page-independent tags live in index.html.
import { useLocation } from 'react-router';
import { site } from '@data/profile';

interface Props {
  title: string;
  description?: string;
  /** Keep search engines out (the resume print page). */
  noindex?: boolean;
}

export default function PageMetaPart({ title, description = site.tagline, noindex = false }: Props) {
  const { pathname } = useLocation();
  // One canonical form per page, whichever way the URL was typed: no trailing
  // slash (the form sitemap.xml lists), except the root.
  const canonicalPath = pathname.length > 1 ? pathname.replace(/\/+$/, '') : pathname;
  const url = new URL(canonicalPath, site.url).href;
  return (
    <>
      <title>{title}</title>
      <meta name="description" content={description} />
      {noindex && <meta name="robots" content="noindex" />}
      <link rel="canonical" href={url} />
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      <meta property="og:url" content={url} />
    </>
  );
}
