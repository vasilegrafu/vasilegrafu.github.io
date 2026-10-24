import { Link } from 'react-router';
import IconPart from '@fx/components/IconPart';
import { sharesToken } from '@fx/lib/tokens';
import IdentityPart from '@modules/shared/IdentityPart';
import PageMetaPart from '@modules/shared/PageMetaPart';
import { experience, projects, skills } from '@data/profile';

const current = experience[0];

// Projects whose tags overlap a skill group's items, e.g. "RAG" or "C# / .NET".
// Derived rather than declared, so a new project shows up here on its own.
const relatedProjects = (items: string[]) => projects.filter((p) => sharesToken(items, p.tags));

export default function SkillsPage() {
  return (
    <>
      <PageMetaPart
        title="Skills — Vasile Grafu"
        description="Skills across AI and machine learning, backend architecture, cloud, engineering leadership, and the fundamentals beneath them."
      />

      <IdentityPart />

      {/* The current stack, pulled straight from the latest role rather than
          curated by hand — so it is the same list the Career page shows.
          Bottom rule only: the identity block above already closes with one,
          and border-y here drew a second line right under it. */}
      <section className="border-line mt-8 border-b pb-6">
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

      {/* One row per role, newest first — the same order as the Career page
          and the profile Background, read here as what each chapter added. */}
      <section className="mt-12">
        <p className="kicker">Over time</p>
        <h2 className="title-section mt-2">What each role added</h2>
        <ol className="border-line relative mt-6 space-y-8 border-s">
          {experience.map((role, i) => {
            const isCurrent = i === 0;
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
