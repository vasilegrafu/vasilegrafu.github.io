// A plain table. The article's prose styles cover headings, lists and code
// but not tables, and these two are the only ones on the site.
//
// Cells take nodes rather than strings so a cell can carry emphasis, and the
// whole thing scrolls sideways on a phone instead of squeezing five columns
// into 390px.
import type { ReactNode } from 'react';

interface Props {
  header: ReactNode[];
  rows: ReactNode[][];
  caption?: ReactNode;
}

export default function TablePart({ header, rows, caption }: Props) {
  return (
    <figure className="my-8">
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-xs">
          <thead>
            <tr className="border-line border-b">
              {header.map((h, i) => (
                <th key={i} className="text-ink px-3 py-2 text-start align-bottom font-semibold">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((r, i) => (
              <tr key={i} className="border-line/60 border-b last:border-0">
                {r.map((c, j) => (
                  <td key={j} className={`px-3 py-2 align-top ${j === 0 ? 'text-ink' : ''}`}>
                    {c}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {caption && <figcaption className="text-faint mt-3 text-xs">{caption}</figcaption>}
    </figure>
  );
}
