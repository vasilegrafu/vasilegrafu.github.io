// A key to the picture above it.
//
// The original of this article pins numbered labels onto the screenshots at
// fixed coordinates. That reads well at one width and badly at every other, so
// here the labels are a list under the picture instead: the same facts, in the
// order you would meet them, and they survive a phone.
import type { ReactNode } from 'react';

export default function MarksPart({ items }: { items: ReactNode[] }) {
  return (
    <div className="card bg-tint/40 my-8 p-5">
      <p className="kicker">What you are looking at</p>
      <ul className="mt-3 space-y-1.5 ps-0 text-xs">
        {items.map((it, i) => (
          <li key={i} className="list-none">
            {it}
          </li>
        ))}
      </ul>
    </div>
  );
}
