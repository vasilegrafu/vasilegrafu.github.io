// The questions, folded away. Nine answers set out in full would be longer
// than the section they follow, and most readers want one of them.
//
// Native <details>, so it works before the JavaScript loads and a browser's
// find-in-page can open the one that matches.
import IconPart from '@fx/components/IconPart';

export default function FaqPart({ items }: { items: [string, string][] }) {
  return (
    <div className="my-8 space-y-3">
      {items.map(([q, a]) => (
        <details key={q} className="card group p-4">
          <summary className="title-card flex cursor-pointer list-none items-center justify-between gap-3">
            {q}
            <IconPart
              name="lucide:chevron-down"
              className="text-accent h-4 w-4 shrink-0 transition-transform group-open:rotate-180"
            />
          </summary>
          <p className="text-muted mt-3 text-xs">{a}</p>
        </details>
      ))}
    </div>
  );
}
