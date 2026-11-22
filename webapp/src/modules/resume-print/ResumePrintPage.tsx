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

/**
 * The stack, one technology per item, set apart by " | " so each one is a unit
 * the eye can pick out. The data writes it comma-separated; a comma inside
 * brackets, as in "AWS (ECS, Fargate)", belongs to that item and is kept.
 */
function Tech({ children }: { children: string }) {
  const items: string[] = [];
  let depth = 0;
  let start = 0;
  for (let i = 0; i < children.length; i++) {
    const c = children[i];
    if (c === '(') depth++;
    else if (c === ')') depth--;
    else if (c === ',' && depth === 0) {
      items.push(children.slice(start, i).trim());
      start = i + 1;
    }
  }
  items.push(children.slice(start).trim());
  // Each technology stays whole on its line ("AWS Bedrock" never breaks after
  // "AWS"); a line breaks only between items.
  return (
    <p className="tech">
      <span className="label">Tech</span>
      {items.map((item, i) => (
        <span key={item}>
          {i > 0 && ' | '}
          <span className="nowrap">{item}</span>
        </span>
      ))}
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
      {resume.summary().map((para) => (
        <p key={para.slice(0, 32)}>{withLinks(para)}</p>
      ))}
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
      <div className="section-intro">
        {os.intro.paragraphs.map((p) => (
          <p key={p}>{p}</p>
        ))}
      </div>
      {os.projects.map((p) => (
        <div key={p.title} className="role keep">
          {/* The project's name leads; its role, year and links follow. */}
          <div className="role-head">
            <h3>
              {p.title} <span className="where">| {p.where}</span>
            </h3>
            <p className="meta">
              {p.meta}
              {p.links.map((l) => (
                <span key={l.href}>
                  {' | '}
                  <a className="link" href={l.href}>
                    {l.label}
                  </a>
                </span>
              ))}
            </p>
          </div>
          <Bullets items={p.bullets} />
          <Tech>{p.tech}</Tech>
        </div>
      ))}

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
