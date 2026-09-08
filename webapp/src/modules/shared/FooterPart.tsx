// Site footer: the header's band mirrored — bar ground, strong line above,
// brand stripe along the bottom edge. Three columns on wide screens: who,
// pages, elsewhere; then a small-print row.
import { Link } from 'react-router';
import IconPart from '@fx/components/IconPart';
import { site } from '@data/profile';
import { navItems } from './nav';

const elsewhere = [
  { href: site.github, label: 'GitHub', icon: 'lucide:github' },
  { href: site.linkedin, label: 'LinkedIn', icon: 'lucide:linkedin' },
  { href: `mailto:${site.email}`, label: 'Email', icon: 'lucide:mail' },
  { href: '/rss.xml', label: 'RSS feed', icon: 'lucide:file-text' },
];

export default function FooterPart() {
  return (
    <footer className="bg-bar border-line-strong border-t">
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid gap-10 sm:grid-cols-2 lg:grid-cols-[1.5fr_1fr_1fr]">
          <div>
            <p className="title-card">{site.name}</p>
            <p className="text-muted mt-2 max-w-xs">
              Engineering leadership, software architecture, and applied AI.
            </p>
            <p className="text-faint mt-4 flex items-center gap-1.5">
              <IconPart name="lucide:map-pin" className="h-4 w-4 shrink-0" />
              {site.location}
            </p>
          </div>

          <nav aria-label="Footer">
            <p className="kicker">Pages</p>
            <ul className="mt-4 space-y-2">
              {navItems.map((item) => (
                <li key={item.href}>
                  <Link to={item.href} className="text-muted hover:text-accent">
                    {item.label}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>

          <div>
            <p className="kicker">Elsewhere</p>
            <ul className="mt-4 space-y-2">
              {elsewhere.map((l) => (
                <li key={l.label}>
                  <a href={l.href} className="text-muted hover:text-accent inline-flex items-center gap-2">
                    <IconPart name={l.icon} className="h-4 w-4 shrink-0" />
                    {l.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <p className="border-line text-faint mt-10 border-t pt-6">
          © {new Date().getFullYear()} {site.name}. All rights reserved.
        </p>
      </div>
      <div className="from-grad-a to-grad-b h-[3px] bg-gradient-to-r" aria-hidden="true" />
    </footer>
  );
}
