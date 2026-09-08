import { Link } from 'react-router';
import { site } from '@data/profile';
import { navItems } from './nav';

export default function FooterPart() {
  return (
    <footer className="border-line border-t">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="flex flex-wrap items-start justify-between gap-6">
          <div>
            <p className="title-card">{site.name}</p>
            <p className="text-faint mt-1 max-w-xs">
              Engineering leadership, software architecture, and applied AI.
            </p>
          </div>
          <nav className="text-muted flex flex-wrap gap-x-4 gap-y-1">
            {navItems.map((item) => (
              <Link key={item.href} to={item.href} className="hover:text-accent">
                {item.label}
              </Link>
            ))}
          </nav>
        </div>
        <p className="text-faint mt-6">
          © {new Date().getFullYear()} {site.name} ·{' '}
          <a href={site.github} className="hover:text-accent">
            GitHub
          </a>{' '}
          ·{' '}
          <a href={site.linkedin} className="hover:text-accent">
            LinkedIn
          </a>{' '}
          ·{' '}
          <a href="/rss.xml" className="hover:text-accent">
            RSS
          </a>
        </p>
      </div>
    </footer>
  );
}
