export interface NavItem {
  href: string;
  label: string;
  icon: string;
}

export const navItems: NavItem[] = [
  { href: '/', label: 'Home', icon: 'lucide:house' },
  { href: '/career/', label: 'Career', icon: 'lucide:briefcase' },
  { href: '/projects/', label: 'Projects', icon: 'lucide:layers' },
  { href: '/articles/', label: 'Articles', icon: 'lucide:file-text' },
  { href: '/contact/', label: 'Contact', icon: 'lucide:at-sign' },
];
