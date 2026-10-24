import { Link } from 'react-router';
import IconPart from '@fx/components/IconPart';
import SegmentBarPart from '@fx/components/SegmentBarPart';
import StatTilePart from '@fx/components/StatTilePart';
import { sharesToken } from '@fx/lib/tokens';
import { yearsOnly } from '@fx/lib/yearsOnly';
import IdentityPart from '@modules/shared/IdentityPart';
import PageMetaPart from '@modules/shared/PageMetaPart';
import {
  careerStart,
  education,
  experience,
  leadershipStart,
  projects,
  skills,
  yearsSince,
} from '@data/profile';
import RoleItemPart from './RoleItemPart';

const current = experience[0];

// Projects whose tags overlap a skill group's items, e.g. "RAG" or "C# / .NET".
// Derived rather than declared, so a project shows up here on its own once the
// projects list has entries again.
const relatedProjects = (items: string[]) => projects.filter((p) => sharesToken(items, p.tags));

const stats = [
  { value: `${yearsSince(careerStart)}+`, label: 'years in software' },
  { value: `${yearsSince(leadershipStart)}`, label: 'years leading teams' },
  { value: '4', label: 'companies' },
];

// Company eras for the ribbon; widths are proportional to duration.
const eras = [
  { label: 'Ubisoft', note: '’05–’08', weight: 3.5 },
  { label: 'TeamNet', note: '’08–’09', weight: 1 },
  { label: 'Consignor', note: '’09–’22', weight: 13 },
  { label: 'nShift', note: '’22–now', weight: 4.7, highlight: true },
];

export default function CareerPage() {
  return (
    <>
      <PageMetaPart
        title="Career — Vasile Grafu"
        description={`${yearsSince(careerStart)}+ years in software: Ubisoft, TeamNet, Consignor, and nShift — from game programming to software architecture, agentic AI and engineering management.`}
      />

      <IdentityPart />

      {/* Two ways to the same resume: read it here, or take the PDF away. The
          print view renders bare — no banner, no nav, no way back — so it opens
          in a tab of its own rather than stranding the reader on a dead end. */}
      <div className="flex flex-wrap items-start justify-end gap-3">
        <a href="/resume-print" target="_blank" rel="noopener noreferrer" className="btn btn-ghost">
          <IconPart name="lucide:file-text" className="h-3.5 w-3.5" />
          View resume
        </a>
        <a href="/cv.pdf" download="Vasile-Grafu-Resume.pdf" className="btn btn-brand">
          <IconPart name="lucide:download" className="h-3.5 w-3.5" />
          Download resume
          <span className="badge bg-accent-ink/20 text-accent-ink">PDF</span>
        </a>
      </div>

      <div className="mt-8 grid grid-cols-3 gap-3 sm:gap-4">
        {stats.map((s) => (
          <StatTilePart key={s.label} value={s.value} label={s.label} />
        ))}
      </div>

      <SegmentBarPart segments={eras} ariaLabel="Career timeline by company" />

      <ol className="border-line relative mt-10 space-y-12 border-s">
        {experience.map((role) => (
          <RoleItemPart key={`${role.company}-${role.position}`} role={role} />
        ))}
      </ol>

      <h2 className="title-section mt-14 flex items-center gap-2.5">
        <IconPart name="lucide:graduation-cap" className="text-accent h-6 w-6" />
        Education
      </h2>
      <ul className="mt-6 space-y-4">
        {education.map((e) => (
          <li key={e.degree}>
            <p className="text-ink font-medium">{e.degree}</p>
            <p className="text-faint">
              {e.school} · {yearsOnly(e.period)}
            </p>
          </li>
        ))}
      </ul>

      {/* The stack, from the Skills page that used to hold it. It belongs after
          the roles: the roles say where the work was done, these say what it was
          done with. The page's own “what each role added” timeline is not
          repeated — every role above already lists its own stack. */}
      <section className="border-line mt-14 border-t pt-10">
        <p className="kicker">Skills in daily use</p>
        <p className="text-muted mt-2 text-xs">
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

      <section className="mt-10">
        <p className="kicker">Skills by area</p>
        <div className="mt-6 grid gap-6 sm:grid-cols-2">
          {skills.map((cat) => {
            const related = relatedProjects(cat.items);
            return (
              <section key={cat.group} className="card card-lift flex flex-col p-5">
                <div className="flex items-center gap-3">
                  <div className="icon-tile">
                    <IconPart name={cat.icon} className="h-5 w-5" />
                  </div>
                  <h3 className="title-card">{cat.group}</h3>
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
                    {related.map((pr, i) => (
                      <span key={pr.title}>
                        {i > 0 && ' · '}
                        <Link to="/projects" className="link-accent">
                          {pr.title}
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
    </>
  );
}
