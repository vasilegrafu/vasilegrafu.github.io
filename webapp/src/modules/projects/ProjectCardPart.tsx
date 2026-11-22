// Project card: icon tile, title, role line, what the system is, what I did
// on it, and tag chips. No key-figures strip — the card stays a plain summary
// for recruiters, with the detail in the "What I did" lines.
import IconPart from '@fx/components/IconPart';
import type { Project } from '@data/profile';

interface Props {
  project: Project;
}

export default function ProjectCardPart({ project }: Props) {
  return (
    <article className="card card-lift flex flex-col p-6">
      <div className="icon-tile mb-3">
        <IconPart name={project.icon} className="h-5 w-5" />
      </div>
      <h2 className="title-item">{project.title}</h2>
      <p className="text-accent mt-1">{project.role}</p>
      <p className="text-muted mt-4">{project.description}</p>
      {project.did && project.did.length > 0 && (
        <div className="mt-5">
          <p className="kicker">What I did</p>
          <ul className="mt-3 space-y-2">
            {project.did.map((d) => (
              <li key={d.label} className="text-muted flex gap-2.5">
                <IconPart name="lucide:check" className="text-accent mt-1 h-4 w-4 shrink-0" />
                <span>
                  <strong className="text-ink font-semibold">{d.label}:</strong> {d.text}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
      <div className="mt-5 flex flex-wrap gap-2">
        {project.tags.map((t) => (
          <span key={t} className="tag">
            {t}
          </span>
        ))}
      </div>
    </article>
  );
}
