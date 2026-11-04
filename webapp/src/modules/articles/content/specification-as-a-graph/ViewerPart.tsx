// One screenshot, filling the screen, with zoom and drag.
//
// These are pictures of an application and the fine print inside them is the
// thing worth looking at, so the article needs a way to look closely. A new
// tab was that way until now; it loses the page, hands the zooming to the
// browser, and comes back scrolled somewhere else. This keeps the reader where
// they were.
//
// It is mounted only while it is open, which is why there is no context, no
// provider and nothing global: the parent holds one piece of state and renders
// this or nothing. The prerendered HTML therefore never contains it, so there
// is nothing here for hydration to disagree about.
//
// The scrim and the controls are fixed light-on-black rather than themed.
// Every other surface on the site follows the theme, but a picture viewer is a
// dark room by convention, and the themed tokens would turn this one white in
// the dark and emerald themes, where ink is near-white.
import { useCallback, useEffect, useRef, useState } from 'react';
import type { MouseEvent as ReactMouseEvent, PointerEvent as ReactPointerEvent } from 'react';
import { createPortal } from 'react-dom';
import IconPart from '@fx/components/IconPart';

const MIN = 1;
const MAX = 8;

/** One press of a zoom button. */
const STEP = 1.4;

/** Where a double click lands, when it is zooming in. */
const NEAR = 2.5;

const clamp = (n: number) => Math.min(MAX, Math.max(MIN, n));

/** Scale, and the offset in screen pixels that goes with it. */
interface View {
  s: number;
  x: number;
  y: number;
}

/** Fitted to the screen and centred. The state the viewer opens in, and the
 *  only state the offset is allowed to be zero in. */
const FIT: View = { s: MIN, x: 0, y: 0 };

// The chrome has to be found before it can be used, and it sits on top of a
// picture that could be any colour — a dark application in one shot, a white
// shopfront in the next. So it is light: a near-white chip with dark glyphs
// inside, which is the one thing that stands out against both the scrim and
// the dark screenshots that fill most of this tour. The shadow is what keeps
// it readable over the two light screenshots, where the chip and the picture
// behind it are nearly the same colour.
//
// Small, though. Contrast is what makes a control findable; size only makes
// it loud, and anything sitting on the picture is in the way of the thing the
// reader opened this for.
const BTN = 'rounded-full p-1.5 text-neutral-900 transition-colors hover:bg-black/10';

const BAR = 'border border-black/10 bg-white/90 shadow-md shadow-black/40 backdrop-blur';

const CLOSE =
  'absolute top-3 right-3 rounded-full bg-white/90 p-1.5 text-neutral-900 shadow-md shadow-black/40 backdrop-blur transition-colors hover:bg-white';

export default function ViewerPart({
  src,
  alt,
  onClose,
}: {
  src: string;
  alt: string;
  onClose: () => void;
}) {
  const [v, setV] = useState<View>(FIT);
  const stage = useRef<HTMLDivElement>(null);
  const pic = useRef<HTMLImageElement>(null);

  /** Every finger or pointer currently down, in the order it arrived. */
  const pts = useRef(new Map<number, { x: number; y: number }>());

  /** Keeps the picture covering the stage: it can be moved only as far as
   *  there is picture hanging off the edge to bring back. Without this a drag
   *  can fling it off the screen entirely, and nothing on screen then says
   *  where it went or how to get it back. */
  const settle = useCallback((p: View): View => {
    const img = pic.current;
    const box = stage.current;
    if (!img || !box) return p;
    const mx = Math.max(0, (img.offsetWidth * p.s - box.clientWidth) / 2);
    const my = Math.max(0, (img.offsetHeight * p.s - box.clientHeight) / 2);
    return { s: p.s, x: Math.min(mx, Math.max(-mx, p.x)), y: Math.min(my, Math.max(-my, p.y)) };
  }, []);

  /** A screen point, measured from the middle of the stage, which is where the
   *  image is centred and so where its transform is measured from too. */
  const at = useCallback((cx: number, cy: number) => {
    const r = stage.current?.getBoundingClientRect();
    return r ? { x: cx - r.left - r.width / 2, y: cy - r.top - r.height / 2 } : { x: 0, y: 0 };
  }, []);

  /** Zoom by a factor, holding the point at (ax, ay) still.
   *
   *  Without the second half of that sentence a zoom is a slider: the picture
   *  grows from its middle and whatever you were looking at slides off the
   *  edge. Holding the pointed-at place still is what makes it feel like
   *  moving closer to the thing you pointed at. */
  const zoomBy = useCallback(
    (k: number, ax = 0, ay = 0) => {
      setV((p) => {
        const s = clamp(p.s * k);
        if (s === p.s) return p;
        if (s === MIN) return FIT;
        const r = s / p.s;
        return settle({ s, x: ax - r * (ax - p.x), y: ay - r * (ay - p.y) });
      });
    },
    [settle],
  );

  /** Drag, but never while the picture is fitted. At 1x there is nothing
   *  outside the frame to go and find, and letting it move only means the
   *  reader can push it off the screen and wonder where it went. */
  const panBy = useCallback(
    (dx: number, dy: number) => {
      setV((p) => (p.s === MIN ? p : settle({ ...p, x: p.x + dx, y: p.y + dy })));
    },
    [settle],
  );

  // Wheel, as a native listener rather than onWheel: React registers wheel
  // handlers passively, and a passive handler cannot call preventDefault, so
  // the page behind would scroll while the picture zoomed.
  useEffect(() => {
    const el = stage.current;
    if (!el) return;
    const wheel = (e: WheelEvent) => {
      e.preventDefault();
      const a = at(e.clientX, e.clientY);
      zoomBy(Math.exp(-e.deltaY * 0.0015), a.x, a.y);
    };
    el.addEventListener('wheel', wheel, { passive: false });
    return () => el.removeEventListener('wheel', wheel);
  }, [at, zoomBy]);

  // Escape closes, and the page behind holds its place while this is open.
  useEffect(() => {
    const key = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    const had = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    document.addEventListener('keydown', key);
    // Focus the dialog rather than the close button: the keyboard still lands
    // inside, and Tab reaches the controls from here, but nothing is left
    // wearing a focus ring the moment a picture opens.
    stage.current?.focus();
    return () => {
      document.body.style.overflow = had;
      document.removeEventListener('keydown', key);
    };
  }, [onClose]);

  const down = (e: ReactPointerEvent<HTMLImageElement>) => {
    e.currentTarget.setPointerCapture(e.pointerId);
    pts.current.set(e.pointerId, { x: e.clientX, y: e.clientY });
  };

  /** Drag with one pointer, pinch with two.
   *
   *  Both are read as a difference from the step before rather than from the
   *  start of the gesture, so neither needs a snapshot of the scale it began
   *  at, and a second finger can join or leave mid-gesture without a jump. The
   *  pinch does both things at once: the distance between the fingers sets the
   *  zoom, the midpoint between them sets the pan. */
  const move = (e: ReactPointerEvent<HTMLImageElement>) => {
    const map = pts.current;
    if (!map.has(e.pointerId)) return;
    const was = [...map.values()];
    map.set(e.pointerId, { x: e.clientX, y: e.clientY });
    const now = [...map.values()];
    if (now.length > 1) {
      const d0 = Math.hypot(was[0].x - was[1].x, was[0].y - was[1].y);
      const d1 = Math.hypot(now[0].x - now[1].x, now[0].y - now[1].y);
      const mid = at((now[0].x + now[1].x) / 2, (now[0].y + now[1].y) / 2);
      if (d0 > 0) zoomBy(d1 / d0, mid.x, mid.y);
      panBy(
        (now[0].x + now[1].x - was[0].x - was[1].x) / 2,
        (now[0].y + now[1].y - was[0].y - was[1].y) / 2,
      );
    } else {
      panBy(e.clientX - was[0].x, e.clientY - was[0].y);
    }
  };

  const up = (e: ReactPointerEvent<HTMLImageElement>) => {
    pts.current.delete(e.pointerId);
  };

  /** Double click, or double tap: in to NEAR at that point, or back to fitted. */
  const toggle = (e: ReactMouseEvent<HTMLImageElement>) => {
    const a = at(e.clientX, e.clientY);
    setV((p) =>
      p.s > MIN ? FIT : settle({ s: NEAR, x: a.x * (1 - NEAR), y: a.y * (1 - NEAR) }),
    );
  };

  return createPortal(
    <div
      ref={stage}
      role="dialog"
      aria-modal="true"
      aria-label={alt}
      tabIndex={-1}
      // A click that lands on the scrim itself closes. Clicks on the picture
      // belong to the picture, and so does a drag, which the pointer capture
      // keeps pointed here even when it ends outside.
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
      className="fixed inset-0 z-50 flex touch-none items-center justify-center overflow-hidden bg-black/90 p-4 outline-none"
    >
      <img
        ref={pic}
        src={src}
        alt={alt}
        draggable={false}
        onPointerDown={down}
        onPointerMove={move}
        onPointerUp={up}
        onPointerCancel={up}
        onDoubleClick={toggle}
        style={{ transform: `translate(${v.x}px, ${v.y}px) scale(${v.s})`, willChange: 'transform' }}
        className={`max-h-full max-w-full select-none ${
          v.s > MIN ? 'cursor-grab active:cursor-grabbing' : 'cursor-zoom-in'
        }`}
      />
      {/* The controls sit over the picture, so the bar itself takes clicks and
          the space around it does not — a click there should reach the scrim
          and close, like anywhere else outside the picture. */}
      <div className="pointer-events-none absolute inset-x-0 bottom-0 flex flex-col items-center gap-2 p-4">
        <div className={`pointer-events-auto flex items-center gap-0.5 rounded-full p-0.5 ${BAR}`}>
          <button
            type="button"
            onClick={() => zoomBy(1 / STEP)}
            aria-label="Zoom out"
            className={BTN}
          >
            <IconPart name="lucide:zoom-out" className="h-4 w-4" />
          </button>
          <button
            type="button"
            onClick={() => setV(FIT)}
            title="Fit to the screen"
            className="min-w-12 rounded-full px-1.5 py-1 text-[11px] font-semibold text-neutral-900 tabular-nums transition-colors hover:bg-black/10"
          >
            {Math.round(v.s * 100)}%
          </button>
          <button type="button" onClick={() => zoomBy(STEP)} aria-label="Zoom in" className={BTN}>
            <IconPart name="lucide:zoom-in" className="h-4 w-4" />
          </button>
        </div>
        <p className={`rounded-full px-2.5 py-0.5 text-[11px] text-neutral-700 ${BAR}`}>
          Scroll or pinch to zoom · drag to move · Esc to close
        </p>
      </div>
      <button
        type="button"
        onClick={onClose}
        aria-label="Close"
        className={CLOSE}
      >
        <IconPart name="lucide:x" className="h-4 w-4" />
      </button>
    </div>,
    document.body,
  );
}
