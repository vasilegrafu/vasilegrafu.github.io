import PageMetaPart from '@modules/shared/PageMetaPart';
import { projects, site } from '@data/profile';
import ProjectCardPart from './ProjectCardPart';

// Lucide icon per project, in the same order as `projects` in profile.ts
const projectIcons = [
  'lucide:bot-message-square', // conversational AI platform
  'lucide:hammer', // AI app builder skill
];

export default function ProjectsPage() {
  return (
    <>
      <PageMetaPart
        title="Projects — Vasile Grafu"
        description="Selected systems: enterprise AI platforms, AI-assisted engineering tooling, and high-throughput web services."
      />

      <p className="kicker">Selected systems</p>
      <h1 className="title-page mt-2">Projects</h1>
      <p className="lede">
        The systems I’m proudest of — what they do, the scale they run at, and the architecture
        behind them.
      </p>

      <div className="mt-8 grid gap-6 sm:grid-cols-2">
        {projects.map((p, i) => (
          <ProjectCardPart key={p.title} project={p} icon={projectIcons[i]} />
        ))}
      </div>

      <p className="text-muted mt-10">
        Open-source experiments and AI demos are coming to this page — watch{' '}
        <a href={site.github} className="link-accent">
          my GitHub
        </a>
        .
      </p>
    </>
  );
}
