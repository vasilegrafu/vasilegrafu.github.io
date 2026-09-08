// Example of a rich component local to this article — an article can import
// any component from its own directory (charts, animations, media…).
import type { ReactNode } from 'react';
import IconPart from '@fx/components/IconPart';

export default function CalloutPart({ children }: { children: ReactNode }) {
  return (
    <aside className="not-prose border-accent-line bg-accent-soft/60 mt-8 flex items-start gap-3 rounded-xl border p-4">
      <IconPart name="lucide:rocket" className="text-accent mt-0.5 h-5 w-5 shrink-0" />
      <span className="text-ink">{children}</span>
    </aside>
  );
}
