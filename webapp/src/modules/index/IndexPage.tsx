import { Link } from 'react-router';
import IconPart from '@fx/components/IconPart';
import PageMetaPart from '@modules/shared/PageMetaPart';
import { careerStart, education, experience, leadershipStart, site, yearsSince } from '@data/profile';

const current = experience[0];

// This page lists roles for orientation, not verification, so it shows years
// alone: "January 2017 – January 2022" reads as "2017 – 2022". The Career page
// and the resume PDF render `period` in full, since those are the surfaces a
// recruiter actually checks. A side with no year ("Present") is kept as-is.
const yearsOnly = (period: string) =>
  period
    .split('–')
    .map((part) => part.match(/\d{4}/)?.[0] ?? part.trim())
    .join(' – ');

// What I own right now, as a definition list rather than a card grid: this is
// the block a recruiter reads to place the role, so it stays dense and factual.
const scope = [
  {
    term: 'Team',
    detail: `The Webservices Team at ${current.company} — hiring, mentoring, and the engineering standards the team works to.`,
  },
  {
    term: 'Systems',
    detail:
      'Dozens of services and full-stack applications distributed across AWS, carrying millions of requests a day.',
  },
  {
    term: 'Architecture',
    detail:
      'Solution architecture, cloud environments and CI/CD pipelines for the applications the team owns.',
  },
  {
    term: 'AI',
    detail:
      'Agentic platform work: LLM orchestration, RAG pipelines and MCP integrations, grounded in company data.',
  },
  {
    term: 'Stack',
    detail: 'C# / .NET, Python / FastAPI, SQL Server, PostgreSQL, AWS, TypeScript, React.',
  },
];

// Three pieces of work, each stated as scope and result rather than as a claim
// about me. The Projects page carries the long form.
const selectedWork = [
  {
    title: 'Conversational AI platform',
    context: 'nShift',
    body: 'Domain-specific agents per department — each with its own prompts, tools and data access — collaborating through an orchestration layer. A continuous pipeline indexes internal documentation, APIs and business data, so answers stay grounded in company-specific information.',
  },
  {
    title: 'Webservices platform',
    context: 'Consignor, then nShift',
    body: 'The core services behind the delivery-management suite: dozens of services and full-stack applications on AWS, serving business-critical delivery workflows around the clock at millions of requests a day.',
  },
  {
    title: 'Two teams at once',
    context: 'Consignor · 2017 – 2022',
    body: 'Ran the Webservices and Integration teams together for a platform serving more than 10,000 business customers — hiring and training the engineers, owning the architecture decisions, and running projects across both.',
  },
];

export default function IndexPage() {
  return (
    <>
      <PageMetaPart
        title={`${site.name} — Engineering Manager, Enterprise & AI Systems`}
        description={`Engineering Manager at ${current.company}, leading the Webservices Team behind services handling millions of requests a day. ${yearsSince(careerStart)} years in software, ${yearsSince(leadershipStart)} years leading teams.`}
      />

      {/* Identity. The banner above already carries the name at full size, so
          this opens with the role instead — the first thing a recruiter needs
          in order to place me. No decorative blooms on this page: the sober
          treatment is the point. */}
      <section className="pt-2 pb-8 sm:pt-4">
        <div className="flex flex-wrap items-start justify-between gap-8 lg:flex-nowrap">
          <div className="max-w-3xl min-w-0">
            <p className="kicker">Profile</p>
            <h1 className="title-page mt-2">
              {current.position} at {current.company}
            </h1>
            <p className="text-faint mt-3 text-xs">
              {site.location} · {yearsSince(careerStart)} years in software ·{' '}
              {yearsSince(leadershipStart)} years leading teams
            </p>

            <p className="mt-6">
              I lead the Webservices Team at {current.company} — the services behind a
              delivery-management platform that connects retailers, 3PLs and manufacturers to more
              than 1,000 carriers across some 190 countries.
            </p>
            <p className="mt-4">
              Thirteen of my years were spent at Consignor, the company {current.company} grew out
              of, first as Technical Lead and then as Team Manager running two teams. Before that,
              game programming at Ubisoft. The work today divides between leadership — hiring,
              mentoring, engineering standards — and hands-on architecture, including the agentic
              AI platform built on top of those services.
            </p>
          </div>
          {/* Monogram: a solid gradient disc with the initials knocked out in
              the accent-ink colour, so it reads as a mark rather than a
              placeholder for a photo. */}
          <div className="hidden shrink-0 items-center justify-center lg:flex" aria-hidden="true">
            <div className="from-grad-a to-grad-b text-accent-ink shadow-accent-solid/30 ring-accent-line flex h-40 w-40 items-center justify-center rounded-full bg-gradient-to-br shadow-xl ring-4">
              <span className="font-display text-5xl font-bold tracking-tight">VG</span>
            </div>
          </div>
        </div>
        {/* One primary action — the resume — and two quiet ones, rather than
            three competing gradient buttons. */}
        <div className="mt-6 flex flex-wrap gap-3">
          <a href="/cv.pdf" download="Vasile-Grafu-Resume.pdf" className="btn btn-brand">
            <IconPart name="lucide:download" className="h-3.5 w-3.5" />
            Download resume
            <span className="badge bg-accent-ink/20 text-accent-ink">PDF</span>
          </a>
          <Link to="/career" className="btn btn-ghost">
            <IconPart name="lucide:briefcase" className="h-3.5 w-3.5" />
            Full career
          </Link>
          <Link to="/contact" className="btn btn-ghost">
            <IconPart name="lucide:at-sign" className="h-3.5 w-3.5" />
            Contact
          </Link>
        </div>
      </section>

      <section className="py-8">
        <p className="kicker">Current scope</p>
        <dl className="divide-line border-line mt-6 divide-y border-y">
          {scope.map((s) => (
            <div key={s.term} className="grid gap-1 py-4 sm:grid-cols-[9rem_1fr] sm:gap-6">
              <dt className="title-card">{s.term}</dt>
              <dd className="text-muted">{s.detail}</dd>
            </div>
          ))}
        </dl>
      </section>

      <section className="py-8">
        <p className="kicker">Selected work</p>
        <ol className="mt-6 space-y-8">
          {selectedWork.map((w) => (
            <li key={w.title}>
              <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
                <h2 className="title-item">{w.title}</h2>
                <span className="text-faint text-xs">{w.context}</span>
              </div>
              <p className="text-muted mt-2 max-w-3xl">{w.body}</p>
            </li>
          ))}
        </ol>
        <p className="text-muted mt-6">
          Longer write-ups on the{' '}
          <Link to="/projects" className="link-accent">
            Projects
          </Link>{' '}
          page.
        </p>
      </section>

      {/* Roles and degrees straight from the profile data, so this list cannot
          drift from the Career page. */}
      <section className="py-8">
        <p className="kicker">Background</p>
        <ul className="mt-6 space-y-3">
          {experience.map((r) => (
            <li
              key={`${r.company}-${r.position}`}
              className="grid gap-x-6 gap-y-1 sm:grid-cols-[8rem_1fr]"
            >
              <span className="text-faint text-xs whitespace-nowrap sm:mt-1">{yearsOnly(r.period)}</span>
              <span>
                <span className="text-ink font-medium">{r.position}</span>
                <span className="text-muted"> · {r.company}</span>
              </span>
            </li>
          ))}
        </ul>

        <p className="kicker mt-10">Education</p>
        <ul className="mt-6 space-y-3">
          {education.map((e) => (
            <li key={e.degree} className="grid gap-x-6 gap-y-1 sm:grid-cols-[8rem_1fr]">
              <span className="text-faint text-xs whitespace-nowrap sm:mt-1">{yearsOnly(e.period)}</span>
              {/* Degree and school on their own lines — the full degree titles
                  are too long to sit on one. */}
              <span>
                <span className="text-ink block font-medium">{e.degree}</span>
                <span className="text-muted block">{e.school}</span>
              </span>
            </li>
          ))}
        </ul>

        <p className="text-muted mt-8">
          Role by role, with what each chapter added, on the{' '}
          <Link to="/career" className="link-accent">
            Career
          </Link>{' '}
          page.
        </p>
      </section>
    </>
  );
}
