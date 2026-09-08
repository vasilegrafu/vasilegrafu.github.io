import IconPart from '@fx/components/IconPart';
import PageMetaPart from '@modules/shared/PageMetaPart';
import { skills } from '@data/profile';

export default function SkillsPage() {
  return (
    <>
      <PageMetaPart
        title="Skills — Vasile Grafu"
        description="Skills across leadership, AI and machine learning, backend architecture, cloud, and the fundamentals beneath them."
      />

      <p className="kicker">Toolbox</p>
      <h1 className="title-page mt-2">Skills</h1>
      <p className="lede">
        What I reach for and the ground it stands on — from leading teams to the math under the
        models.
      </p>

      <div className="mt-8 grid gap-6 sm:grid-cols-2">
        {skills.map((cat) => (
          <section key={cat.group} className="card card-lift p-5">
            <div className="flex items-center gap-3">
              <div className="icon-tile">
                <IconPart name={cat.icon} className="h-5 w-5" />
              </div>
              <h2 className="title-card">{cat.group}</h2>
            </div>
            <p className="text-muted mt-3">{cat.blurb}</p>
            <ul className="mt-4 flex flex-wrap gap-2">
              {cat.items.map((item) => (
                <li key={item} className="chip">
                  {item}
                </li>
              ))}
            </ul>
          </section>
        ))}
      </div>
    </>
  );
}
