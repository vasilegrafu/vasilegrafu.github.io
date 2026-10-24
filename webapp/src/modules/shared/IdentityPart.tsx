// What I am now, above the page it heads.
//
// No name here: the banner, the footer and the page title already carry it, and
// on a page plainly about my career a third repetition says nothing. The label
// does the work instead — it marks this line as the present tense, against the
// roles below it that run back to 2005.
//
// Rendered by the Career page, which is the only page that states the title.
import { site } from '@data/profile';

export default function IdentityPart() {
  return (
    <div className="border-line mb-8 border-b pb-6">
      <p className="kicker">Currently</p>
      {/* Between the two steps the scale offers: title-card's weight and face,
          one size up. text-xl (title-section) shouted at 85 characters, body
          size disappeared. */}
      <p className="title-card mt-2 text-lg text-balance">{site.title}</p>
    </div>
  );
}
