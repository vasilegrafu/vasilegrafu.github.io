// Whatever is in webapp/version.json, rendered as a table, followed by when the
// site was built. The fields are not hard-coded: add a key to the file and it
// shows up here. Kept out of the sitemap and noindex, and linked from nowhere —
// this is for checking what is deployed, not for readers.
import PageMetaPart from '@modules/shared/PageMetaPart';
import version from '../../../version.json';

/** Substituted at build time by `define` in vite.config.ts, already formatted. */
declare const __BUILD_TIME__: string;

const rows: [string, string][] = [
  ...Object.entries(version).map(([key, value]): [string, string] => [key, String(value)]),
  ['built', __BUILD_TIME__],
];

export default function VersionPage() {
  return (
    <>
      <PageMetaPart title="Version — Vasile Grafu" description="Build version." noindex />

      <p className="kicker">Build</p>
      <h1 className="title-page mt-2">Version</h1>

      <dl className="divide-line border-line mt-8 divide-y border-y">
        {rows.map(([key, value]) => (
          <div key={key} className="grid gap-1 py-4 sm:grid-cols-[10rem_1fr] sm:gap-6">
            <dt className="title-card">{key}</dt>
            <dd className="text-muted tabular-nums">{value}</dd>
          </div>
        ))}
      </dl>
    </>
  );
}
