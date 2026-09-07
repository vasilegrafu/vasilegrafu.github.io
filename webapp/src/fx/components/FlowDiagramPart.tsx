// Small architecture flow diagram: labeled steps joined by arrows inside a
// tinted panel. Fully data-driven — pass the step labels and an optional note.
import { Fragment } from 'react';
import IconPart from './IconPart';

interface Props {
  steps: string[];
  note?: string;
  ariaLabel?: string;
}

export default function FlowDiagramPart({ steps, note, ariaLabel }: Props) {
  return (
    <div className="bg-tint border-line rounded-lg border p-3" role="img" aria-label={ariaLabel}>
      <div className="flex flex-wrap items-center gap-x-1.5 gap-y-2">
        {steps.map((step, i) => (
          <Fragment key={step}>
            {i > 0 && (
              <IconPart name="lucide:arrow-right" className="text-faint h-3.5 w-3.5 shrink-0" />
            )}
            <span className="border-accent-line bg-surface text-ink rounded-md border px-2.5 py-1 text-xs font-medium">
              {step}
            </span>
          </Fragment>
        ))}
      </div>
      {note && <p className="text-faint mt-2 text-xs">{note}</p>}
    </div>
  );
}
