import PageMetaPart from '@modules/shared/PageMetaPart';

// A placeholder, for now. The write-ups are being redone: they render from
// `projects` in src/data/profile.ts, which is empty, and the card that renders
// one is still in ProjectCardPart.tsx. Put entries back and restore the list
// that git history holds to bring this page to life again.
export default function ProjectsPage() {
  return (
    <>
      <PageMetaPart title="Projects — Vasile Grafu" description="Selected systems — on the way." />

      <p className="text-muted">Nothing here yet. Write-ups are on the way.</p>
    </>
  );
}
