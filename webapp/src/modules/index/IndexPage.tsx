import { Link } from 'react-router';
import IconPart from '@fx/components/IconPart';
import PageMetaPart from '@modules/shared/PageMetaPart';
import { careerStart, leadershipStart, site, yearsSince } from '@data/profile';

// A Now page, not a profile: what I am working on and thinking about this
// month. The biography lives on the Career page, one click away.
//
const companyName = 'nShift';

// Two projects, stated at length. A Now page that lists everything is a
// portfolio wearing a different hat; two things described properly say more
// about how someone thinks than ten things listed.
const work = [
  {
    n: '01',
    kicker: 'Application Builder',
    title: 'Give the model a shape to follow',
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
    note: 'An article on this is on the way.',
  },
  {
    n: '02',
    kicker: 'Product Specs Builder',
    title: 'Specifications as a graph',
    icon: 'lucide:workflow',
    body: [
      'A specification is not a document. It is one problem looked at from several angles at once — the requirements, the components, the screens, a prototype you can click. Each is a different point of view on the same thing.',
      'The trouble is that they drift. Change a requirement and the screens still describe the old one. The skill I am building holds all of it as a single graph, so a change made in one view propagates to the others instead of quietly leaving them wrong. You write a specification to solve a problem; the graph is what keeps every view of that problem telling the same story.',
    ],
    points: [
      'Requirements, components, screens and prototype as one connected graph.',
      'Edit one view and the AI carries the change through the rest.',
      'No silent drift between what was asked for and what was drawn.',
    ],
    note: null,
  },
];

// Open questions, stated as questions. These are the invitation: an unfinished
// thought is far easier to reply to than a finished claim.
const onMyMind = [
  'How much of a specification can be checked mechanically, and where does judgement have to stay human?',
  'What does engineering management look like when the manager still writes a large share of the code?',
  'Whether MCP holds up as an integration surface once it meets enterprise data.',
  'What thirteen years of carrier-integration infrastructure already knew that AI tooling keeps rediscovering.',
];

export default function IndexPage() {
  return (
    <>
      <PageMetaPart
        title={`${site.name} — Controlling vibe coding`}
        description="Two projects: an application builder that holds agents to a known shape, and specifications kept as a graph so every view of a problem stays in step."
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
          {w.note && (
            <p className="mt-5">
              <span className="badge">{w.note}</span>
            </p>
          )}
        </section>
      ))}

      <section className="border-line border-t pt-10 pb-8">
        <p className="kicker">Also on my mind</p>
        <ul className="mt-6 space-y-4">
          {onMyMind.map((q) => (
            <li key={q} className="border-line-strong flex gap-3 border-s-2 ps-4">
              <IconPart name="lucide:lightbulb" className="text-accent mt-1 h-4 w-4 shrink-0" />
              <span className="text-muted">{q}</span>
            </li>
          ))}
        </ul>
        <p className="text-muted mt-6">
          If you are working on any of this, I’d like to hear from you —{' '}
          <Link to="/contact" className="link-accent">
            say hello
          </Link>
          .
        </p>
      </section>

      {/* One quiet factual line. The home page carries the most inbound weight
          of any page on the site; stripping the identity out of it entirely
          would throw that away. The full story is on the Career page. */}
      <section className="border-line border-t pt-6 pb-8">
        <p className="text-faint text-xs">
          {site.name} · Engineering Manager at {companyName} · {yearsSince(careerStart)} years in
          software · {yearsSince(leadershipStart)} years leading teams · {site.location}
        </p>
        <p className="text-muted mt-3">
          The record is on the{' '}
          <Link to="/career" className="link-accent">
            Career
          </Link>{' '}
          page.
        </p>
      </section>
    </>
  );
}
