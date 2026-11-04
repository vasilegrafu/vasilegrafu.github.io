// The five steps of one change, each with the diagram that belongs to it.
//
// The boxes in the five diagrams do not move between steps — only the colours
// change — so reading them in order shows the change travelling through the
// graph rather than five unrelated pictures. They are drawn at their own size,
// like every other diagram here, so their labels match.
import { asset, diagramWidth, sizeOf } from './assets';

export interface Step {
  name: string;
  title: string;
  text: string;
  alt: string;
}

export default function StepsPart({ steps }: { steps: Step[] }) {
  return (
    <ol className="my-8 list-none space-y-10 ps-0">
      {steps.map((s, i) => {
        const [w, h] = sizeOf(s.name);
        return (
          <li key={s.name}>
            <div className="flex items-baseline gap-3">
              <span className="text-faint font-display text-xs tabular-nums">
                {String(i + 1).padStart(2, '0')}
              </span>
              <p className="title-card">{s.title}</p>
            </div>
            <p className="text-muted mt-2">{s.text}</p>
            <div className="border-line mx-auto mt-4 w-fit max-w-full overflow-hidden rounded-xl border bg-white p-3">
              <a
                href={asset(s.name)}
                target="_blank"
                rel="noopener noreferrer"
                className="block no-underline"
              >
                <img
                  src={asset(s.name)}
                  alt={s.alt}
                  width={w}
                  height={h}
                  loading="lazy"
                  style={{ width: diagramWidth(s.name) }}
                  className="block h-auto max-w-full"
                />
              </a>
            </div>
          </li>
        );
      })}
    </ol>
  );
}
