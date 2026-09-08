import { Link } from 'react-router';
import IconPart from '@fx/components/IconPart';
import { sharesToken } from '@fx/lib/tokens';
import PageMetaPart from '@modules/shared/PageMetaPart';
import { experience, projects, skills } from '@data/profile';

const current = experience[0];

// Oldest role first, so the toolbox reads in the order it was built.
const eras = [...experience].reverse();

// Projects whose tags overlap a skill group's items, e.g. "RAG" or "C# / .NET".
// Derived rather than declared, so a new project shows up here on its own.
const relatedProjects = (items: string[]) => projects.filter((p) => sharesToken(items, p.tags));

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

      {/* The current stack, pulled straight from the latest role rather than
          curated by hand — so it is the same list the Career page shows. */}
      <section className="border-line mt-8 border-y py-6">
        <p className="kicker">In daily use</p>
        <p className="text-muted mt-2">
          The stack behind my current work as {current.position} at {current.company}.
        </p>
        <ul className="mt-4 flex flex-wrap gap-2">
          {current.tech?.map((t) => (
            <li key={t} className="chip">
              <IconPart name="lucide:check" className="text-accent h-4 w-4 shrink-0" />
              {t}
            </li>
          ))}
        </ul>
      </section>

      <section className="mt-8">
        <p className="kicker">By area</p>
        <div className="mt-6 grid gap-6 sm:grid-cols-2">
          {skills.map((cat) => {
            const related = relatedProjects(cat.items);
            return (
              <section key={cat.group} className="card card-lift flex flex-col p-5">
                <div className="flex items-center gap-3">
                  <div className="icon-tile">
                    <IconPart name={cat.icon} className="h-5 w-5" />
                  </div>
                  <h2 className="title-card">{cat.group}</h2>
                </div>
                <p className="text-muted mt-2">{cat.blurb}</p>
                <ul className="mt-4 flex flex-wrap gap-2">
                  {cat.items.map((item) => (
                    <li key={item} className="chip">
                      {item}
                    </li>
                  ))}
                </ul>
                {related.length > 0 && (
                  <p className="text-faint mt-auto pt-4">
                    Applied in{' '}
                    {related.map((p, i) => (
                      <span key={p.title}>
                        {i > 0 && ' · '}
                        <Link to="/projects" className="link-accent">
                          {p.title}
                        </Link>
                      </span>
                    ))}
                  </p>
                )}
              </section>
            );
          })}
        </div>
      </section>

      {/* One row per role, oldest first: the same data the Career page tells
          as a story, read here as what each chapter added to the toolbox. */}
      <section className="mt-12">
        <p className="kicker">Over time</p>
        <h2 className="title-section mt-2">How the toolbox grew</h2>
        <ol className="border-line relative mt-6 space-y-8 border-s">
          {eras.map((role, i) => {
            const isCurrent = i === eras.length - 1;
            return (
              <li key={`${role.company}-${role.period}`} className="relative ps-6">
                <span
                  className={
                    isCurrent
                      ? 'bg-accent-solid absolute top-2 -start-[5px] h-2.5 w-2.5 rounded-full'
                      : 'bg-line-strong absolute top-2 -start-[5px] h-2.5 w-2.5 rounded-full'
                  }
                  aria-hidden="true"
                />
                <p className="text-faint">{role.period}</p>
                <h3 className="title-card mt-1">
                  {role.position} · {role.company}
                </h3>
                <ul className="mt-3 flex flex-wrap gap-2">
                  {role.tech?.map((t) => (
                    <li key={t} className="tag">
                      {t}
                    </li>
                  ))}
                </ul>
              </li>
            );
          })}
        </ol>
      </section>

      <p className="text-muted mt-10">
        The roles behind these are on the{' '}
        <Link to="/career" className="link-accent">
          career page
        </Link>
        , and the systems they built on the{' '}
        <Link to="/projects" className="link-accent">
          projects page
        </Link>
        .
      </p>
    </>
  );
}
