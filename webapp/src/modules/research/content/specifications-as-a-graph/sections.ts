// The article's sections, named once.
//
// Both the contents list at the top and the headings themselves are built
// from this, so a section cannot be renamed out of step with the link to it,
// and the list cannot fall out of the order the article is actually in. The
// ids come from the titles, so they are stable as long as the wording is —
// and they are what an outside link to a section would use.
export const SECTIONS = {
  problem: 'The problem today',
  solution: 'A solution: specifications as a graph',
  idea: 'The idea: small facts, linked',
  parts: 'Three parts: a skill, an application, two interfaces',
  tour: 'See it working',
  how: 'How it works',
  change: 'A change, step by step',
  roles: 'What each role gets',
  compare: 'Compared with what you use today',
  questions: 'Questions people ask',
  try: 'Try it',
} as const;

export const slug = (title: string) =>
  title
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');
