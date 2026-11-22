// Print source for public/cv.pdf, rendered from src/data/resume.ts (the
// resume's own content) and the contact details in src/data/profile.ts.
// Regenerate the PDF after any change with:
//   npm run build
//   npm run preview   (note the port it prints)
//   & "C:\Program Files\Google\Chrome\Application\chrome.exe" --headless=new --disable-gpu `
//     --virtual-time-budget=10000 `
//     --no-pdf-header-footer --print-to-pdf="<repo>\webapp\public\cv.pdf" "http://localhost:4173/resume-print"
// --virtual-time-budget is not optional: without it Chrome prints before the
// web fonts have loaded, roughly half the time, and the fallback metrics
// rewrap every line and change the pagination. With the flag the output is
// byte-identical run to run, so if two renders of the same content differ,
// the flag was missing.
//
// One column throughout, so applicant-tracking systems read the PDF top to
// bottom in order. This page renders outside the site shell, is noindex, and
// stays out of the sitemap.
import type { ReactNode } from 'react';
import PageMetaPart from '@modules/shared/PageMetaPart';
import { site } from '@data/profile';
import { resume, type ResumeBullet } from '@data/resume';
import './resume-print.css';

const linkedinLabel = site.linkedin.replace('https://www.', '');
const githubLabel = site.github.replace('https://', '');
const siteLabel = site.url.replace('https://', '');

/** Text with [label](url) links in it, as the resume data writes them. */
function withLinks(text: string): ReactNode[] {
  const parts: ReactNode[] = [];
  const re = /\[([^\]]+)\]\(([^)]+)\)/g;
  let last = 0;
  for (const m of text.matchAll(re)) {
    if (m.index > last) parts.push(text.slice(last, m.index));
    parts.push(
      <a key={m.index} className="link" href={m[2]}>
        {m[1]}
      </a>,
    );
    last = m.index + m[0].length;
  }
  if (last < text.length) parts.push(text.slice(last));
  return parts;
}

function Bullets({ items }: { items: ResumeBullet[] }) {
  return (
    <ul>
      {items.map((b) => (
        <li key={b.text}>
          {b.lead && <b>{b.lead}</b>} {withLinks(b.text)}
        </li>
      ))}
    </ul>
  );
}

function Tech({ children }: { children: string }) {
  return (
    <p className="tech">
      <span className="label">Tech</span>
      {children}
    </p>
  );
}

export default function ResumePrintPage() {
  const os = resume.openSource;
  return (
    <div className="resume-print">
      <PageMetaPart title={`${site.name} — Resume`} noindex />

      <header>
        <h1>{site.name}</h1>
        <div className="headline">{resume.headline}</div>
        <div className="contact">
          {site.location} | {site.phone} | {site.email} |{' '}
          <a className="link" href={site.linkedin}>
            {linkedinLabel}
          </a>{' '}
          |{' '}
          <a className="link" href={site.github}>
            {githubLabel}
          </a>{' '}
          |{' '}
          <a className="link" href={site.url}>
            {siteLabel}
          </a>
        </div>
      </header>

      <h2>Summary</h2>
      <p>{resume.summary()}</p>
      <p className="industry">
        <b>Industry:</b> {resume.industry()}
      </p>
      <p className="industry-next">
        <b>Languages:</b> {resume.languages}
      </p>

      <h2>Skills</h2>
      <div className="skills">
        {resume.skills.map((s) => (
          <p key={s.label}>
            <b>{s.label}:</b> {s.text}
          </p>
        ))}
      </div>

      <h2>Open Source (Research)</h2>
      <div className="role keep">
        <div className="role-head">
          <p className="meta">
            {os.meta}
            {os.links.map((l) => (
              <span key={l.href}>
                {' | '}
                <a className="link" href={l.href}>
                  {l.label}
                </a>
              </span>
            ))}
          </p>
          <h3>
            {os.title} <span className="where">| {os.where}</span>
          </h3>
        </div>
        <Bullets items={os.bullets} />
        <Tech>{os.tech}</Tech>
      </div>

      <h2>Experience</h2>
      {resume.roles.map((role) => (
        <div key={`${role.company}-${role.position}`} className="role">
          <div className="role-head">
            <p className="meta">
              {role.period} | {role.location}
            </p>
            <h3>
              {role.position} <span className="where">| {role.company}</span>
            </h3>
          </div>
          {role.about && <p className="about">{role.about}</p>}
          <Bullets items={role.bullets} />
          {role.projects && (
            <>
              <p className="projects-label">
                <span className="label">Key projects</span>
              </p>
              {role.projects.map((p) => (
                <div key={p.name} className="project">
                  <p className="proj-head">
                    <b className="pname">{p.name}:</b> {p.context}
                  </p>
                  <Bullets items={p.bullets} />
                </div>
              ))}
            </>
          )}
          <Tech>{role.tech}</Tech>
        </div>
      ))}

      <div className="role earlier">
        <div className="role-head">
          <h3>Earlier career</h3>
        </div>
        {resume.earlier.map((e) => (
          <p key={e.title}>
            <b>{e.title}</b> <span className="meta">({e.period})</span>: {e.text}
          </p>
        ))}
      </div>

      <h2>Education</h2>
      {resume.education.map((e) => (
        <p key={e.degree}>
          <b>{e.degree}</b>, {e.school} <span className="nowrap">({e.period})</span>
        </p>
      ))}
    </div>
  );
}
