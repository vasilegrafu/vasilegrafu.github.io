// Where this article's pictures live. They sit in public/ rather than in this
// directory because they are referenced by absolute path and never processed:
// the diagrams are SVG straight from the tool that drew them, and the
// screenshots were taken at 2560px and written out at 1600px as WebP.
export const BASE = '/articles/specification-as-a-graph';

export const asset = (name: string) => `${BASE}/${name}`;

// Every diagram's own size, taken from the width and height its file declares.
//
// All twelve set their labels at 10.5 units and their titles at 13, so what a
// label measures on screen depends entirely on how wide the diagram is drawn.
// Stretched to fill the column they came out at anything from 11px to 19px —
// drift, the narrowest at 670 units, printed its labels larger than the body
// text beside it. So a diagram is not fitted to the column at all. It is drawn
// at whatever width puts its labels at LABEL px, and centred in the space
// left over.
//
// Two of them, overview and parts, are wide enough that even that is more
// room than there is; they fall back to the column and land near 9px. Every
// other diagram is exact.
//
// The sizes also reserve the right box before the picture loads, so a lazy
// image further down the page does not shove the text under the cursor.
export const DIAGRAMS: Record<string, [number, number]> = {
  'change-1.svg': [1194, 464],
  'change-2.svg': [1194, 464],
  'change-3.svg': [1194, 464],
  'change-4.svg': [1194, 464],
  'change-5.svg': [1194, 464],
  'drift.svg': [670, 424],
  'graph.svg': [1233, 312],
  'idea.svg': [1222, 394],
  'overview.svg': [1409, 328],
  'parts.svg': [1375, 332],
  'readers.svg': [989, 412],
  'talked.svg': [856, 708],
};

/** Every screenshot was written out at the same size. */
export const SHOT: [number, number] = [1600, 1000];

export const sizeOf = (name: string): [number, number] => DIAGRAMS[name] ?? SHOT;

/** What a diagram's labels should measure on screen, against 15px body text. */
const LABEL = 10;

/** What the diagrams set their labels at, in their own units. */
const LABEL_UNITS = 10.5;

/** The width to draw a diagram at, so its labels come out at LABEL px. */
export const diagramWidth = (name: string) =>
  Math.round((DIAGRAMS[name]?.[0] ?? 0) * (LABEL / LABEL_UNITS));
