/** A URL without its scheme or leading www, for showing a link as readable text. */
export const bareUrl = (url: string) => url.replace(/^https?:\/\/(www\.)?/, '').replace(/\/$/, '');
