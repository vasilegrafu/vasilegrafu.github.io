import IconPart from '@fx/components/IconPart';
import SegmentBarPart from '@fx/components/SegmentBarPart';
import StatTilePart from '@fx/components/StatTilePart';
import { yearsOnly } from '@fx/lib/yearsOnly';
import IdentityPart from '@modules/shared/IdentityPart';
import PageMetaPart from '@modules/shared/PageMetaPart';
import { careerStart, education, experience, leadershipStart, yearsSince } from '@data/profile';
import RoleItemPart from './RoleItemPart';

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
    </>
  );
}
