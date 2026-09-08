// Bordered card with an icon tile and title; body text goes in children.
// Used for the "What I do" grid on the home page and similar grids.
import type { ReactNode } from 'react';
import IconPart from './IconPart';

interface Props {
  icon: string;
  title: string;
  children: ReactNode;
}

export default function IconCardPart({ icon, title, children }: Props) {
  return (
    <div className="card card-lift p-5">
      <div className="icon-tile">
        <IconPart name={icon} className="h-5 w-5" />
      </div>
      <h2 className="title-card mt-3">{title}</h2>
      <p className="text-muted mt-2">{children}</p>
    </div>
  );
}
