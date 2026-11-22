import PageMetaPart from '@modules/shared/PageMetaPart';
import { projects } from '@data/profile';
import ProjectCardPart from './ProjectCardPart';

// The systems I built at nShift, from `projects` in src/data/profile.ts, in
// the order given there. Written for recruiters and employers: what each one
// does and my part in it, without the depth Articles and Research go into.
export default function ProjectsPage() {
  return (
    <>
      <PageMetaPart
        title="Projects — Vasile Grafu"
        description="Systems I designed and built at nShift: an AI assistant inside nShift’s products, an enterprise MCP gateway for AI agents, and the services behind addresses, pricing and file delivery."
      />

      <h1 className="title-page">Selected Projects</h1>
      <p className="lede">
        Systems I designed and built at nShift: what each one does, and my part in it.
      </p>

      <div className="mt-8 grid gap-6">
        {projects.map((p) => (
          <ProjectCardPart key={p.title} project={p} />
        ))}
      </div>
    </>
  );
}
