import IconPart from '@fx/components/IconPart';
import SegmentBarPart from '@fx/components/SegmentBarPart';
import StatTilePart from '@fx/components/StatTilePart';
import PageMetaPart from '@modules/shared/PageMetaPart';
import { education, experience } from '@data/profile';
import RoleItemPart from './RoleItemPart';

const stats = [
  { value: '20+', label: 'years in software' },
  { value: '18', label: 'years leading teams' },
  { value: '4', label: 'companies' },
];

// Company eras for the ribbon; widths are proportional to duration.
const eras = [
  { label: 'Ubisoft', note: '’05–’08', weight: 3.5 },
  { label: 'TeamNet', note: '’08–’09', weight: 1 },
  { label: 'Consignor', note: '’09–’22', weight: 13 },
  { label: 'nShift', note: '’22–now', weight: 4.7, highlight: true },
];

// Lucide icon per role, in the same order as `experience`.
const roleIcons = [
  'lucide:sparkles', // nShift — AI era
  'lucide:globe', // Consignor Team Manager
  'lucide:layers', // Consignor Technical Lead
  'lucide:package', // TeamNet — ERP
  'lucide:gamepad-2', // Ubisoft
];

export default function CareerPage() {
  return (
    <>
      <PageMetaPart
        title="Career — Vasile Grafu"
        description="20+ years in software: Ubisoft, TeamNet, Consignor, and nShift — from game programming to engineering management and AI systems."
      />

      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="kicker">Journey</p>
          <h1 className="title-page mt-2">Career</h1>
          <p className="lede">The roles I’ve held, the teams I’ve built, and what each chapter added.</p>
        </div>
        <a href="/cv.pdf" download="Vasile-Grafu-Resume.pdf" className="btn btn-primary">
          <IconPart name="lucide:download" className="h-3.5 w-3.5" />
          Download resume (PDF)
        </a>
      </div>

      <div className="mt-8 grid grid-cols-3 gap-3 sm:gap-4">
        {stats.map((s) => (
          <StatTilePart key={s.label} value={s.value} label={s.label} />
        ))}
      </div>

      <SegmentBarPart segments={eras} ariaLabel="Career timeline by company" />

      <ol className="border-line relative mt-10 space-y-12 border-s">
        {experience.map((role, i) => (
          <RoleItemPart key={`${role.company}-${role.position}`} role={role} icon={roleIcons[i]} />
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
              {e.school} · {e.period}
            </p>
          </li>
        ))}
      </ul>
    </>
  );
}
