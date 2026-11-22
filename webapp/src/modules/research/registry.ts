// Research registry — the single list of all research entries and their
// metadata. Each entry lives in content/<id>/ResearchPart.tsx (plus any local
// components, scripts, or media its directory needs).
//
// This list is the only place an entry has to be registered: routes.ts expands
// /research/:id from it, the build prerenders one page per entry, and
// sitemap.xml is generated from it. Unlike articles, entries are not in
// rss.xml — the feed is Articles only, for now.
export interface ResearchMeta {
  id: string;
  title: string;
  description: string;
  pubDate: Date;
  tags: string[];
  /**
   * The introduction on the Research list card, a short paragraph. Optional:
   * without it the card shows `description`, which stays short because it is
   * also the meta and social-preview description (keep that near 160 chars).
   */
  summary?: string[];
  /**
   * A 640×400 picture for the list card, by absolute path into public/ — the
   * entry's own folder there, under thumbs/. Optional: without it the card is
   * text only.
   */
  thumbnail?: string;
  /** What the thumbnail shows, for screen readers. */
  thumbnailAlt?: string;
  /**
   * An entry that lives elsewhere — a video series, say. The card links out
   * to it, in a new tab, and the entry has no page of its own: no
   * content/<id>/, nothing prerendered, nothing in sitemap.xml.
   */
  href?: string;
  /** The card's call to action. Defaults to "Read the full piece". */
  cta?: string;
}

export const research: ResearchMeta[] = [
  {
    id: 'specs-builder-tutorial-series',
    title: 'specs-builder: the tutorial series',
    description:
      'A five-episode tutorial series on YouTube: specs-builder, specifications as a graph, built with AI, step by step.',
    pubDate: new Date('2026-11-22'),
    tags: ['Video', 'Tutorial', 'AI-assisted development', 'Product specification'],
    thumbnail: '/research/specs-builder-tutorial-series/thumbs/cover.jpg',
    thumbnailAlt: 'The series cover: specs-builder, specification as a graph, five episodes',
    summary: [
      'Specifications as a graph, on video. In five episodes I build a specification with specs-builder, step by step, together with an AI assistant: describing the product in plain words, watching it become a graph of small, linked facts, and reading it in the browser.',
    ],
    href: 'https://www.youtube.com/playlist?list=PLAlCi-PFDpyk',
    cta: 'Watch the series on YouTube',
  },
  {
    id: 'specifications-as-a-graph',
    title: 'Specifications as a graph',
    description:
      'A product specification held as a graph of small, linked facts: an AI assistant writes it with you, people read it in a browser, agents build from it, and every change shows what it touches before it is made.',
    pubDate: new Date('2026-11-04'),
    tags: ['AI-assisted development', 'Product specification', 'Agentic architectures'],
    thumbnail: '/research/specifications-as-a-graph/around.png',
    thumbnailAlt: 'One requirement in the graph, with the rule, roles, screens and evidence linked to it',
    summary: [
      'Specifications as a graph helps you write a product specification together with an AI assistant: you describe the product in plain words, and it writes the requirements, rules, screens and a clickable prototype with you, asking about whatever you left open. Everything is held as small, linked facts rather than pages of prose, so nothing is written twice. People read it in a browser, coding agents build from the same files, and before any fact changes, the graph shows everything that change will touch.',
    ],
  },
];

export const researchByDate = () =>
  [...research].sort((a, b) => b.pubDate.valueOf() - a.pubDate.valueOf());
