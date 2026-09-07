// Large clickable contact channel card: icon tile, title, subtitle, hover arrow.
import IconPart from './IconPart';

interface Props {
  href: string;
  icon: string;
  title: string;
  subtitle: string;
}

export default function LinkCardPart({ href, icon, title, subtitle }: Props) {
  return (
    <a href={href} className="card card-lift group hover:border-accent flex items-center gap-4 p-5">
      <span className="icon-tile h-11 w-11 shrink-0">
        <IconPart name={icon} className="h-5 w-5" />
      </span>
      <span className="min-w-0 grow">
        <span className="font-display text-ink block font-semibold">{title}</span>
        <span className="text-muted block truncate text-sm">{subtitle}</span>
      </span>
      <span
        className="text-faint group-hover:text-accent shrink-0 transition-all group-hover:translate-x-1"
        aria-hidden="true"
      >
        →
      </span>
    </a>
  );
}
