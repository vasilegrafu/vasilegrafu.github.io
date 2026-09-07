/** "31 August 2026" — the date form used on the listing and the article page. */
export const formatDate = (d: Date) =>
  d.toLocaleDateString('en-GB', { year: 'numeric', month: 'long', day: 'numeric' });
