import PageMetaPart from '@modules/shared/PageMetaPart';

// A placeholder, for now. The listing renders from `articles` in registry.ts,
// which is empty: put an entry back there and restore the list that git history
// holds to bring this page to life again. rss.xml and sitemap.xml are generated
// from the same registry, so both stay valid while it is empty.
export default function ArticlesPage() {
  return (
    <>
      <PageMetaPart
        title="Articles — Vasile Grafu"
        description="Writing on software architecture, applied AI, and engineering leadership."
      />

      <p className="text-muted">Nothing here yet. Articles are on the way.</p>
    </>
  );
}
