// Print source for public/cv.pdf, rendered entirely from src/data/profile.ts.
// Regenerate the PDF after any profile change with:
//   npm run build
//   npm run preview   (note the port it prints)
//   & "C:\Program Files\Google\Chrome\Application\chrome.exe" --headless=new --disable-gpu `
//     --no-pdf-header-footer --print-to-pdf="<repo>\webapp\public\cv.pdf" "http://localhost:4173/resume-print"
// This page renders outside the site shell, is noindex, and stays out of the sitemap.
import { Fragment } from 'react';
import PageMetaPart from '@modules/shared/PageMetaPart';
import { education, experience, projects, site, skills } from '@data/profile';
import './resume-print.css';

const keyProject = projects[0];

const linkedinLabel = site.linkedin.replace('https://www.', '');
const siteLabel = site.url.replace('https://', '');
const telHref = `tel:${site.phone.replace(/\s/g, '')}`;

// Read in the first few seconds, so it leads with figures rather than prose.
const highlights = [
  'Millions of requests served every day by the platform my team runs',
  '10,000+ business clients on the systems I have led',
  '50 web services in production, distributed across AWS',
  '20+ years, from real-time game engines to agentic AI systems',
];

/** Bullets are written as "Lead-in: detail" — split so the lead-in can be bold. */
function splitBullet(b: string) {
  const i = b.indexOf(': ');
  return i > 0 ? { title: b.slice(0, i), rest: b.slice(i + 2) } : { title: null, rest: b };
}

export default function ResumePrintPage() {
  return (
    <div className="resume-print">
      <PageMetaPart title={`${site.name} — Resume`} noindex />

      <header>
        <h1>{site.name}</h1>
        <div className="subtitle">{site.title}</div>
        <div className="contact">
          <span>{site.location}</span>
          <span>
            <a href={telHref}>{site.phone}</a>
          </span>
          <span>
            <a href={`mailto:${site.email}`}>{site.email}</a>
          </span>
          <span>
            <a href={site.linkedin}>{linkedinLabel}</a>
          </span>
          <span>
            <a href={site.url}>{siteLabel}</a>
          </span>
        </div>
      </header>

      <h2>Summary</h2>
      <p>{site.intro}</p>

      <div className="highlights">
        {highlights.map((h) => (
          <div key={h}>{h}</div>
        ))}
      </div>

      <h2>Skills</h2>
      <div className="skills">
        {skills.map((s) => (
          <p key={s.group}>
            <b>{s.group}:</b> {s.items.join(', ')}
          </p>
        ))}
      </div>

      <h2>Experience</h2>
      {experience.map((role) => {
        // The Career page carries every bullet; the PDF takes the leading few
        // when a role sets pdfBullets, which caps how long the resume can grow.
        const bullets = role.pdfBullets ? role.bullets.slice(0, role.pdfBullets) : role.bullets;
        return (
          <div
            key={`${role.company}-${role.position}`}
            className={bullets.length > 5 ? 'role allow-break' : 'role'}
          >
            <div className="role-head">
              <h3>
                {role.position} · {role.company}, {role.location}
              </h3>
              <span className="period">{role.period}</span>
            </div>
            {role.aboutShort && <p className="about">{role.aboutShort}</p>}
            {role.summary && <p className="summary">{role.summary}</p>}
            <ul>
              {bullets.map((b) => {
                const { title, rest } = splitBullet(b);
                return (
                  <li key={b}>
                    {title ? (
                      <Fragment>
                        <b>{title}:</b> {rest}
                      </Fragment>
                    ) : (
                      b
                    )}
                  </li>
                );
              })}
            </ul>
            {role.tech && (
              <p className="tech">
                <span className="tech-label">Tech</span>
                {role.tech.join(' · ')}
              </p>
            )}
          </div>
        );
      })}

      <h2>Key Project</h2>
      <div className="role">
        <div className="role-head">
          <h3>{keyProject.title}</h3>
          <span className="period">{keyProject.role}</span>
        </div>
        <p className="summary">{keyProject.description}</p>
      </div>

      <h2>Education</h2>
      {education.map((e) => (
        <div key={e.degree} className="edu">
          <b>{e.degree}</b> — {e.school} <span className="period">({e.period})</span>
        </div>
      ))}
    </div>
  );
}
