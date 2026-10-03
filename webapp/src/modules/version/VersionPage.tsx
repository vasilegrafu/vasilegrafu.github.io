// Whatever is in webapp/version.json, rendered as a table. The fields are not
// hard-coded: add a key to the file and it shows up here. Kept out of the
// sitemap and noindex — this is for checking what is deployed, not for readers.
import PageMetaPart from '@modules/shared/PageMetaPart';
import version from '../../../version.json';

export default function VersionPage() {
  return (
    <>
      <PageMetaPart title="Version — Vasile Grafu" description="Build version." noindex />

      <p className="kicker">Build</p>
      <h1 className="title-page mt-2">Version</h1>

      <dl className="divide-line border-line mt-8 divide-y border-y">
        {Object.entries(version).map(([key, value]) => (
          <div key={key} className="grid gap-1 py-4 sm:grid-cols-[10rem_1fr] sm:gap-6">
            <dt className="title-card">{key}</dt>
            <dd className="text-muted tabular-nums">{String(value)}</dd>
          </div>
        ))}
      </dl>
    </>
  );
}
