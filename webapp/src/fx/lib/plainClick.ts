/** Wraps an in-page action so it only takes over a plain left click.
 *
 *  Middle clicks and modified clicks fall through to the browser untouched, so
 *  an anchor that opens something inside the page still opens its href in a new
 *  tab for anyone who asks for that — which is worth keeping, because it is the
 *  only way to get a picture onto a second screen. */
import type { MouseEvent } from 'react';

export const plainClick =
  (act: () => void) =>
  (e: MouseEvent<HTMLElement>) => {
    if (e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    e.preventDefault();
    act();
  };
