// Project card: icon tile, title, role line, description, optional diagram,
// and tag chips.
import type { ReactNode } from 'react';
import IconPart from '@fx/components/IconPart';
import type { Project } from '@data/profile';

interface Props {
  project: Project;
  icon: string;
  diagram?: ReactNode;
}

export default function ProjectCardPart({ project, icon, diagram }: Props) {
  return (
    <article className="card card-lift flex flex-col p-6">
      <div className="icon-tile mb-3">
        <IconPart name={icon} className="h-5 w-5" />
      </div>
      <h2 className="title-item">{project.title}</h2>
      <p className="text-accent mt-1">{project.role}</p>
      {project.outcomes && (
        <dl className="bg-tint mt-4 grid gap-3 rounded-lg p-3 sm:grid-cols-3">
          {project.outcomes.map((o) => (
            <div key={o.label}>
              <dd className="title-card">{o.value}</dd>
              <dt className="text-faint text-xs">{o.label}</dt>
            </div>
          ))}
        </dl>
      )}
      <p className="text-muted mt-4 grow">{project.description}</p>
      {diagram && <div className="mt-4">{diagram}</div>}
      <div className="mt-4 flex flex-wrap gap-2">
        {project.tags.map((t) => (
          <span key={t} className="tag">
            {t}
          </span>
        ))}
      </div>
    </article>
  );
}
