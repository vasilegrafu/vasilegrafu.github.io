export interface NavItem {
  href: string;
  label: string;
  icon: string;
}

// Order is the argument the site makes about itself: what I am working on and
// thinking about comes first, and the record of where I have been comes after.
// "Now" rather than "Profile" because the front page is a dated snapshot of
// current work, not a biography — the biography is on Career.
export const navItems: NavItem[] = [
  { href: '/', label: 'Now', icon: 'lucide:sprout' },
  { href: '/articles', label: 'Articles', icon: 'lucide:file-text' },
  { href: '/career', label: 'Career', icon: 'lucide:briefcase' },
  { href: '/projects', label: 'Projects', icon: 'lucide:layers' },
  { href: '/contact', label: 'Contact', icon: 'lucide:at-sign' },
];
