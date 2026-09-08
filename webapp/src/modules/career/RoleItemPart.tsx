// One entry on the Career timeline: era icon, period badge, company context,
// role summary, a numbered list of what I did, and tech chips.
import IconPart from '@fx/components/IconPart';
import { cx } from '@fx/lib/cx';
import type { Role } from '@data/profile';

interface Props {
  role: Role;
  icon: string;
}

export default function RoleItemPart({ role, icon }: Props) {
  return (
    <li className="ms-6">
      <span className="border-line bg-bg text-accent absolute -start-3.5 mt-1 flex h-7 w-7 items-center justify-center rounded-full border">
        <IconPart name={icon} className="h-4 w-4" />
      </span>
      <p className="text-faint flex flex-wrap items-center gap-2">
        <span className="badge">{role.period}</span>
        {role.location}
      </p>
      <h2 className="title-item mt-2">
        {role.position} · {role.company}
      </h2>
      {role.about && (
        <p className="text-faint border-line-strong mt-3 border-s-2 ps-3.5">
          {role.about}
        </p>
      )}
      {role.summary && <p className="text-muted mt-3">{role.summary}</p>}
      <div className="mt-5 grid gap-x-10 gap-y-5 sm:grid-cols-2">
        {role.bullets.map((b, i) => {
          const idx = b.indexOf(': ');
          const title = idx > 0 ? b.slice(0, idx) : null;
          const rest = idx > 0 ? b.slice(idx + 2) : b;
          const body = title ? rest.charAt(0).toUpperCase() + rest.slice(1) : rest;
          // Leading bullets name the teams I ran — scope, not activity — so their
          // numeral takes the accent colour to set them apart from the rest.
          const lead = i < (role.leadBullets ?? 0);
          return (
            <div key={b} className="flex gap-3">
              <span
                className={cx(
                  'font-display pt-px font-bold tabular-nums',
                  lead ? 'text-accent' : 'text-label/70',
                )}
              >
                {String(i + 1).padStart(2, '0')}
              </span>
              <div>
                {title && <p className="title-card">{title}</p>}
                <p className={cx('text-muted', title && 'mt-0.5')}>
                  {body}
                </p>
              </div>
            </div>
          );
        })}
      </div>
      {role.tech && (
        <div className="mt-4 flex flex-wrap gap-2">
          {role.tech.map((t) => (
            <span key={t} className="tag">
              {t}
            </span>
          ))}
        </div>
      )}
    </li>
  );
}
