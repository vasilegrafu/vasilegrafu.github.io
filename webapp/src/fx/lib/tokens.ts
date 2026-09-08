// Loose keyword matching between short labels — "C# / .NET, ASP.NET Core"
// against "C# / .NET" — so lists written for people can be cross-referenced
// without a second, hand-maintained index of ids.

/** Words too generic to count as a match on their own. */
const STOP = new Set([
  'and',
  'the',
  'of',
  'for',
  'in',
  'with',
  'code',
  'design',
  'development',
  'foundations',
  'generation',
  'principles',
  'server',
  'skill',
  'software',
  'web',
]);

/** Lower-cased, singularised words of a label; "C#", ".NET" and "CI/CD" survive. */
export function tokenize(label: string): string[] {
  return label
    .toLowerCase()
    .split(/[^a-z0-9#+.]+/)
    .map((t) => t.replace(/^\.+|\.+$/g, ''))
    .map((t) => (t.length > 3 && t.endsWith('s') ? t.slice(0, -1) : t))
    .filter((t) => t.length > 1 && !STOP.has(t));
}

/** True when any label in `a` shares a meaningful word with any label in `b`. */
export function sharesToken(a: string[], b: string[]): boolean {
  const seen = new Set(a.flatMap(tokenize));
  return b.some((label) => tokenize(label).some((t) => seen.has(t)));
}
