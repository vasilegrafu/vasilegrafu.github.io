// Name and what I do, above the page it heads.
//
// The name leads and the title supports it, one step down — the other way
// round reads as a job advert. Neither is set large: the banner above already
// carries the site's voice, and this block only has to say who is speaking.
//
// Anything passed as children sits at the far end of the same line, so the
// page's own actions read as part of the heading rather than as a second row
// beneath it. On a narrow window they wrap under the title instead.
//
// Rendered by the Career page, which is the only page that states the title.
import type { ReactNode } from 'react';
import { site } from '@data/profile';

export default function IdentityPart({ children }: { children?: ReactNode }) {
  return (
    <div className="border-line mb-8 flex flex-wrap items-center justify-between gap-4 border-b pb-6">
      <div>
        <p className="title-card text-lg">{site.name}</p>
        <p className="text-muted text-card mt-1 text-balance">{site.title}</p>
      </div>
      {children}
    </div>
  );
}
