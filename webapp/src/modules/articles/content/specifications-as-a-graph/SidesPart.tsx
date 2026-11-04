// The same fact, six times over, in six places that do not know about each
// other.
//
// This is the article's premise and it is worth showing rather than stating.
// Six tiles, each holding its own wording of one rule, each with a dashed
// border and nothing drawn between them — the eye reads the repetition and
// the absence of any line joining it up before the sentence underneath
// explains either.
import IconPart from '@fx/components/IconPart';

const sides = [
  {
    icon: 'lucide:file-text',
    name: 'The requirements document',
    holds: '“a cart holds up to five of a product”',
  },
  { icon: 'lucide:globe', name: 'A page in the wiki', holds: '“max 5 per line”' },
  { icon: 'lucide:palette', name: 'The design file', holds: 'a quantity field, 1–5' },
  { icon: 'lucide:monitor', name: 'The prototype', holds: 'a dropdown, 1 to 5' },
  { icon: 'lucide:layers', name: 'The tracker', holds: '“limit 5” in a ticket' },
  { icon: 'lucide:code-xml', name: 'The code and its tests', holds: 'MAX_PER_LINE = 5' },
];

export default function SidesPart() {
  return (
    <figure className="my-8">
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {sides.map((s) => (
          <div key={s.name} className="border-line-strong rounded-xl border border-dashed p-4">
            <div className="flex items-center gap-2">
              <IconPart name={s.icon} className="text-faint h-4 w-4 shrink-0" />
              <p className="title-card">{s.name}</p>
            </div>
            <p className="mt-2.5">
              <span className="chip">{s.holds}</span>
            </p>
          </div>
        ))}
      </div>
      <figcaption className="text-faint mt-3 text-xs">
        One rule, six places, six wordings — and not one line between them. Nothing here points at
        anything else here.
      </figcaption>
    </figure>
  );
}
