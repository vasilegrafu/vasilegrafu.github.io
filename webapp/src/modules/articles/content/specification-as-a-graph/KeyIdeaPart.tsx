// The one paragraph to take away if you read nothing else.
import type { ReactNode } from 'react';
import IconPart from '@fx/components/IconPart';

export default function KeyIdeaPart({ children }: { children: ReactNode }) {
  return (
    <aside className="border-accent-line bg-accent-soft/60 my-8 flex items-start gap-3 rounded-xl border p-5">
      <IconPart name="lucide:lightbulb" className="text-accent mt-0.5 h-5 w-5 shrink-0" />
      <div>
        <p className="kicker">The key idea</p>
        <p className="text-ink mt-2">{children}</p>
      </div>
    </aside>
  );
}
