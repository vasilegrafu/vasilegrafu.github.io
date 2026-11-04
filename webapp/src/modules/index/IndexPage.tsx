import { Link } from 'react-router';
import IconPart from '@fx/components/IconPart';
import PageMetaPart from '@modules/shared/PageMetaPart';
import { site } from '@data/profile';

// A Now page, not a profile: what I am working on and thinking about this
// month. The biography lives on the Career page, one click away.
//
// Two projects, stated at length. A Now page that lists everything is a
// portfolio wearing a different hat; two things described properly say more
// about how someone thinks than ten things listed. Each block is an
// introduction to a longer piece of writing — one written, one to come.
const work = [
  {
    n: '01',
    kicker: 'Product Specs Builder',
    title: 'Specifications as a graph',
    icon: 'lucide:workflow',
    body: [
      'A product owner changes one number: a cart could hold five of a product, and now it holds six. Two weeks later the product page still stops at five, a test still expects five, and an agent has just built a new screen that says five too. Nobody did anything wrong. The number was written in too many places, and nobody could see them all.',
      'A specification is not a document. It is one problem looked at from several angles at once — the requirements, the rules, the screens, a prototype you can click — and the angles drift apart the moment one of them changes. So I am building it as a graph instead: many small facts, each written once, each linked to the facts that depend on it. Change one, and the graph names everything that change touches before you make it.',
      'People read it in a browser. AI agents build from the same files, and they build only what changed. Nothing is copied between the two, so neither can be looking at a version the other has not seen.',
    ],
    points: [
      'Requirements, rules, screens and prototype as one connected graph.',
      'The impact of a change, shown before the change is made.',
      'One source for people and for the agents doing the building.',
    ],
    article: 'specification-as-a-graph',
    note: null,
  },
  {
    n: '02',
    kicker: 'Application Builder',
    title: 'Controlling vibe coding',
    icon: 'lucide:hammer',
    body: [
      'Vibe coding lets a model invent an application, and it invents a different one every time you ask. The builder takes the invention out of the structure and leaves it only in the subject.',
      'You hand it a template — an application whose shape is already known and already works — and the agent builds that same shape in another domain. The architecture is given; the domain is the variable. What comes back is predictable, because the only thing the model decided was the part you wanted it to decide.',
    ],
    points: [
      'Templates carry the shape: structure, boundaries, the way the pieces fit.',
      'The agent follows the shape and changes the domain, not the architecture.',
      'Predictable output, because the model is choosing far less than it looks.',
    ],
    article: null,
    note: 'An article on this is on the way.',
  },
];

export default function IndexPage() {
  return (
    <>
      <PageMetaPart
        title={`${site.name} — Now`}
        description="Two projects: specifications kept as a graph so every view of a problem stays in step, and an application builder that holds agents to a known shape."
      />

      {work.map((w, i) => (
        // No rule above the first one: with the page opening straight into it,
        // a top border would draw a line directly under the nav bar.
        <section
          key={w.n}
          className={i === 0 ? 'pt-2 pb-8 sm:pt-4' : 'border-line border-t pt-10 pb-8'}
        >
          <div className="flex items-baseline gap-3">
            <span className="text-faint font-display text-xs tabular-nums">{w.n}</span>
            <p className="kicker">{w.kicker}</p>
          </div>
          <h2 className="title-section mt-3 flex items-start gap-2.5">
            <IconPart name={w.icon} className="text-accent mt-1 h-5 w-5 shrink-0" />
            {w.title}
          </h2>
          <div className="mt-4 max-w-3xl space-y-3">
            {w.body.map((p) => (
              <p key={p.slice(0, 24)} className="text-muted">
                {p}
              </p>
            ))}
          </div>
          <ul className="mt-5 space-y-2">
            {w.points.map((pt) => (
              <li key={pt} className="flex gap-2.5">
                <IconPart name="lucide:check" className="text-accent mt-1 h-4 w-4 shrink-0" />
                <span className="text-muted">{pt}</span>
              </li>
            ))}
          </ul>
          {w.article && (
            <p className="mt-6">
              <Link to={`/articles/${w.article}`} className="btn btn-ghost">
                Read the article
                <IconPart name="lucide:arrow-right" className="h-3.5 w-3.5" />
              </Link>
            </p>
          )}
          {w.note && (
            <p className="mt-5">
              <span className="badge">{w.note}</span>
            </p>
          )}
        </section>
      ))}

      <section className="border-line border-t pt-8 pb-8">
        <p className="text-muted">
          If you are working on anything like this, I’d like to hear from you —{' '}
          <Link to="/contact" className="link-accent">
            say hello
          </Link>
          .
        </p>
      </section>
    </>
  );
}
