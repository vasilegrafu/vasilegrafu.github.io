import { Link } from 'react-router';
import IconCardPart from '@fx/components/IconCardPart';
import IconPart from '@fx/components/IconPart';
import StatTilePart from '@fx/components/StatTilePart';
import PageMetaPart from '@modules/shared/PageMetaPart';
import { experience, site } from '@data/profile';

const current = experience[0];

// Reach and practice: three figures, then how the work is actually done. The
// lifecycle detail sits in the hero sentence above, so one tile points at it
// rather than spending six. The AI tiles say what I build and how I build —
// they describe the systems and the practice, never me.
const scaleStats = [
  { value: '20+', label: 'years in software development' },
  { value: '50+', label: 'applications built or contributed to' },
  { value: 'Millions', label: 'of requests a day on some applications' },
  { value: 'Every phase', label: 'specification through production' },
  { value: 'AI systems', label: 'built, not just used' },
  { value: 'AI-assisted', label: 'engineering, every day' },
];

// Written from the employer's point of view rather than mine — one line each,
// stating a benefit rather than restating a fact the tiles above already carry.
const valueProps = [
  {
    icon: 'lucide:rocket',
    title: 'Teams that ship',
    body: 'Cohesive teams delivering business-critical software, year after year.',
  },
  {
    icon: 'lucide:wrench',
    title: 'Leadership that builds',
    body: 'An architect’s judgment, from someone who still writes the code.',
  },
  {
    icon: 'lucide:workflow',
    title: 'Fewer handoff gaps',
    body: 'Someone who has worked every phase sees what falls between them.',
  },
  {
    icon: 'lucide:lightbulb',
    title: 'AI that pays off',
    body: 'Grounded in production experience, not in hype.',
  },
  {
    icon: 'lucide:gauge',
    title: 'Built for load',
    body: 'Systems that stay up when the business depends on them.',
  },
  {
    icon: 'lucide:sprout',
    title: 'People who grow',
    body: 'Engineers hired, mentored and kept — the team outlasts the system.',
  },
];

// What keeps me in this work, as opposed to what I am paid to do.
const principles = [
  {
    icon: 'lucide:telescope',
    title: 'Curiosity',
    body: 'I’m naturally driven to understand how things work and why they work the way they do. I enjoy going deep into a problem, learning from first principles, and connecting ideas across different areas. For me, the process of understanding is rewarding in itself.',
  },
  {
    icon: 'lucide:trending-up',
    title: 'Constant evolution',
    body: 'I’m always looking for ways to improve how I think, work, and build. AI-assisted engineering has already reshaped my daily practice, and I actively explore new tools, ideas, and approaches that can make me more effective. I see change as an opportunity to rethink what’s possible rather than simply adapt to it.',
  },
  {
    icon: 'lucide:handshake',
    title: 'Teams that discover',
    body: 'I do my best work in supportive, collaborative teams where people learn from each other, challenge ideas constructively, and take pride in their craft. I value working toward a shared goal while giving everyone the space to contribute, experiment, and grow.',
  },
  {
    icon: 'lucide:target',
    title: 'Impact',
    body: 'Technology is most interesting to me when it matters — when the systems we build carry real businesses, save people time, and open possibilities that weren’t there before. Understanding why the work matters shapes how I build it, and seeing an idea become something people rely on every day is the most satisfying part of engineering.',
  },
];

export default function IndexPage() {
  return (
    <>
      <PageMetaPart title="Vasile Grafu — Engineering Manager & AI Systems Builder" />

      <section className="relative py-10 sm:py-14">
        <div className="pointer-events-none absolute inset-0 -z-10" aria-hidden="true">
          <div className="blob bg-blob-a -top-24 -right-24 h-80 w-80"></div>
          <div className="blob bg-blob-b top-32 -left-24 h-64 w-64"></div>
        </div>
        <div className="flex flex-wrap items-center justify-between gap-8 lg:flex-nowrap">
          <div className="max-w-3xl min-w-0">
            <p className="text-accent font-medium">Hello, I’m</p>
            <h1 className="title-hero mt-1">{site.name}</h1>
            <p className="text-muted mt-3 text-xl">{site.title}</p>
            <p className="mt-5 text-lg leading-relaxed">{site.intro}</p>
          </div>
          <div className="hidden shrink-0 items-center justify-center lg:flex" aria-hidden="true">
            <div className="from-grad-a to-grad-b shadow-accent-solid/20 rounded-full bg-gradient-to-br p-1 shadow-xl">
              <div className="bg-bg flex h-36 w-36 items-center justify-center rounded-full">
                <span className="font-display from-grad-a to-grad-b bg-gradient-to-br bg-clip-text text-4xl font-bold text-transparent">
                  VG
                </span>
              </div>
            </div>
          </div>
        </div>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link to="/career" className="btn btn-primary">
            My career story
          </Link>
          <Link to="/articles" className="btn btn-ghost">
            Read my writing
          </Link>
        </div>
      </section>

      <section className="py-8">
        <p className="kicker">Reach and practice</p>
        {/* A strip between hairlines rather than a card grid, so the facts read
            differently from the capability cards below. */}
        <div className="border-line mt-5 grid grid-cols-2 gap-x-6 gap-y-8 border-y py-8 sm:grid-cols-3 sm:gap-x-10">
          {scaleStats.map((s) => (
            <StatTilePart key={s.label} value={s.value} label={s.label} bare />
          ))}
        </div>
      </section>

      <section className="py-8">
        <p className="kicker">What I do</p>
        <div className="mt-4 grid gap-6 sm:grid-cols-2">
          <IconCardPart icon="lucide:code-xml" title="Hands-on engineering">
            I still write the code: C#/.NET, Python, React, SQL, and the AWS infrastructure it runs
            on. Specifications, architecture, cloud environments, CI/CD pipelines — I build them, not
            just approve them.
          </IconCardPart>
          <IconCardPart icon="lucide:users" title="Engineering leadership">
            Leading one of {current.company}’s core teams — hiring, mentoring, and setting the
            standards behind business-critical delivery software.
          </IconCardPart>
          <IconCardPart icon="lucide:hammer" title="AI-assisted engineering">
            Advanced Claude Code skills, including an app builder that reads existing codebases
            through a structural snapshot and generates, migrates, or translates applications with
            verified results.
          </IconCardPart>
          <IconCardPart icon="lucide:sparkles" title="AI systems">
            Agentic AI platforms: LLM orchestration, RAG pipelines, and multi-agent architectures
            grounded in real business data, integrated over MCP and answerable in production.
          </IconCardPart>
        </div>
      </section>

      <section className="py-8">
        <p className="kicker">Working with me</p>
        <h2 className="title-section mt-2">What I bring to an organization</h2>
        {/* The only panel on a page of strips, cards and lists — that shape is
            enough to mark the zone, so the colour stays out of it. */}
        <div className="bg-tint border-line mt-4 grid gap-8 rounded-2xl border p-8 sm:grid-cols-2 lg:grid-cols-3">
          {valueProps.map((v) => (
            <div key={v.title}>
              <div className="icon-tile">
                <IconPart name={v.icon} className="h-5 w-5" />
              </div>
              <h3 className="font-display text-ink mt-4 text-lg font-semibold">{v.title}</h3>
              <p className="text-muted mt-1.5 text-sm leading-relaxed">{v.body}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="py-8">
        <p className="kicker">Principles</p>
        <h2 className="title-section mt-2">What drives me</h2>
        {/* A numbered manifesto rather than another card grid — principles are not
            features, and the form should say so before the words do. */}
        <div className="mt-6 grid gap-x-12 gap-y-9 sm:grid-cols-2">
          {principles.map((p) => (
            <div key={p.title} className="flex gap-4">
              <IconPart name={p.icon} className="text-label mt-0.5 h-6 w-6 shrink-0" />
              <div>
                <h3 className="font-display text-ink font-semibold">{p.title}</h3>
                <p className="text-muted mt-1.5 text-sm leading-relaxed">{p.body}</p>
              </div>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}
