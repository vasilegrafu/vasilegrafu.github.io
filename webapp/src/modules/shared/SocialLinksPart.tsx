// Mail / GitHub / LinkedIn icon links shown in the header.
import IconPart from '@fx/components/IconPart';
import { site } from '@data/profile';

const links = [
  { href: `mailto:${site.email}`, label: 'Email', tip: 'Send me an email', icon: 'lucide:mail' },
  { href: site.github, label: 'GitHub', tip: 'My code on GitHub', icon: 'lucide:github' },
  { href: site.linkedin, label: 'LinkedIn', tip: 'My LinkedIn profile', icon: 'lucide:linkedin' },
];

export default function SocialLinksPart() {
  return (
    <div className="text-faint flex items-center gap-3">
      {links.map((l) => (
        <a key={l.label} href={l.href} aria-label={l.label} data-tip={l.tip} className="tip hover:text-accent">
          <IconPart name={l.icon} className="h-4.5 w-4.5" />
        </a>
      ))}
    </div>
  );
}
