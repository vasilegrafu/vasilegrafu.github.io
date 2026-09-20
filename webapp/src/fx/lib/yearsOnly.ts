/**
 * Strips a period down to its years: "January 2017 – January 2022" becomes
 * "2017 – 2022". A side with no year survives as written, which is what keeps
 * "Present" intact.
 *
 * The site stores full month-year periods and renders this shorter form where
 * the reader wants orientation rather than verification.
 */
export const yearsOnly = (period: string) =>
  period
    .split('–')
    .map((part) => part.match(/\d{4}/)?.[0] ?? part.trim())
    .join(' – ');
