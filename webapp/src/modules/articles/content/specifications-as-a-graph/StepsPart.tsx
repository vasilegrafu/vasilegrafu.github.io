// The five steps of one change, each with the diagram that belongs to it.
//
// The boxes in the five diagrams do not move between steps — only the colours
// change — so reading them in order shows the change travelling through the
// graph rather than five unrelated pictures. That makes the colours the whole
// point of the sequence, which is why these in particular are drawn into the
// page: reviewed and needs review have to read as themselves on any theme.
import { STEP_LABEL } from './assets';
import DiagramPart from './DiagramPart';

export interface Step {
  name: string;
  title: string;
  text: string;
  /** What the diagram is showing — the colours that moved since the step
      before, said in a line, because five near-identical pictures are hard to
      read against each other without being told where to look. */
  watch: string;
  alt: string;
}

export default function StepsPart({ steps }: { steps: Step[] }) {
  return (
    <ol className="my-8 list-none space-y-8 ps-0">
      {steps.map((s, i) => (
        <li key={s.name}>
          <div className="flex items-baseline gap-3">
            <span className="text-faint font-display text-xs tabular-nums">
              {String(i + 1).padStart(2, '0')}
            </span>
            <p className="title-card">{s.title}</p>
          </div>
          <p className="text-muted mt-2">{s.text}</p>
          <div className="mt-3">
            <DiagramPart name={s.name} alt={s.alt} label={STEP_LABEL} />
          </div>
          <p className="text-faint mt-2 text-xs">
            <span className="text-label font-semibold">In the picture: </span>
            {s.watch}
          </p>
        </li>
      ))}
    </ol>
  );
}
