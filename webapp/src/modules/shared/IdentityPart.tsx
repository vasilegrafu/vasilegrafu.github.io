// Name and what I do, above the page it heads.
//
// The name leads and the title supports it, one step down — the other way
// round reads as a job advert. Neither is set large: the banner above already
// carries the site's voice, and this block only has to say who is speaking.
//
// Rendered by the Career page, which is the only page that states the title.
import { site } from '@data/profile';

export default function IdentityPart() {
  return (
    <div className="border-line mb-8 border-b pb-6">
      <p className="title-card text-lg">{site.name}</p>
      <p className="text-muted text-card mt-1 text-balance">{site.title}</p>
    </div>
  );
}
