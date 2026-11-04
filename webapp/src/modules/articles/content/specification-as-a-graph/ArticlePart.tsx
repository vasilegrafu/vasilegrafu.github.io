import CardsPart from './CardsPart';
import ContentsPart from './ContentsPart';
import FaqPart from './FaqPart';
import FigurePart from './FigurePart';
import GalleryPart, { type Shot } from './GalleryPart';
import KeyIdeaPart from './KeyIdeaPart';
import MarksPart from './MarksPart';
import ScenarioPart from './ScenarioPart';
import SectionPart from './SectionPart';
import { SECTIONS } from './sections';
import SidesPart from './SidesPart';
import StepsPart, { type Step } from './StepsPart';
import TablePart from './TablePart';

// The tour of the application, in the order a first visit takes. You start on
// the front page and open the whole graph; then you follow one requirement
// through its links, its tests and the screens that show it; the last two show
// what a change looks like from the inside.
const shots: Shot[] = [
  {
    name: 'overview.png',
    kicker: 'Document',
    title: 'The front page',
    alt: 'The front page of the Voltline specification',
    caption:
      'Where every reader starts. What the product is, how big the specification is, and what is still open.',
  },
  {
    name: 'graph.png',
    kicker: 'Graph',
    title: 'The whole specification',
    alt: 'The graph view, with one bubble per kind of node',
    caption:
      'Each bubble is one kind of node, sized by how many there are. Each line shows how many links join two kinds.',
  },
  {
    name: 'graph-card.png',
    kicker: 'Graph',
    title: 'A right-click opens a card',
    alt: 'A summary card for one node, opened from the graph',
    caption:
      'A short summary without leaving the graph. Every ID in the card opens the next card, so you can walk from fact to fact.',
  },
  {
    name: 'layers.png',
    kicker: 'Graph',
    title: 'The layers',
    alt: 'Every node arranged in layers, goals on the left and components on the right',
    caption:
      'All of it in layers, goals on the left and components on the right. You can follow one goal to every part that serves it.',
  },
  {
    name: 'layers-flow.png',
    kicker: 'Graph',
    title: 'The layers of one flow',
    alt: 'The layer view narrowed to a single flow',
    caption:
      'One flow — buying a product — selected. Only the goals, requirements, endpoints and screens that flow uses.',
  },
  {
    name: 'requirement.png',
    kicker: 'Requirements',
    title: 'One requirement',
    alt: 'Requirement R4 in full, with its evidence and open question',
    caption:
      'R4 in full: what it says, where it came from, how sure the specification is, and the question still open about it.',
  },
  {
    name: 'criteria.png',
    kicker: 'Requirements',
    title: 'Its tests, in plain words',
    alt: 'Acceptance criteria written as given, when, then',
    caption:
      'Each acceptance criterion is given, when, then. Builder agents turn these lines straight into automated tests.',
  },
  {
    name: 'design.png',
    kicker: 'Design',
    title: 'The design system',
    alt: 'The design system: colours, fonts and spacing',
    caption:
      'The colours, fonts and spacing every screen follows. Agents read the same thing as a file of design tokens.',
  },
  {
    name: 'prototype.png',
    kicker: 'Design',
    title: 'A working prototype',
    alt: 'A working prototype of a product page',
    caption:
      'A real page, built from the screen’s description and the design system. Viewable at phone, tablet or desktop size.',
  },
  {
    name: 'wireframe.png',
    kicker: 'Design',
    title: 'Every element explained',
    alt: 'The same page with every element labelled',
    caption:
      'The same page with every element labelled: which component it is, and which requirement it serves.',
  },
  {
    name: 'matrix.png',
    kicker: 'Matrix',
    title: 'What links to what',
    alt: 'A matrix of every kind of node against every other kind',
    caption:
      'Every kind of node against every other, each cell counting the links. An empty cell is often a gap.',
  },
  {
    name: 'stale.png',
    kicker: 'Change',
    title: 'After a change, what needs review',
    alt: 'The list of nodes that need review after a change',
    caption:
      'Five became six. Everything that depends on what changed is listed, with the old and the new words, until someone reviews it.',
  },
];

const steps: Step[] = [
  {
    name: 'change-1.svg',
    title: 'You ask, and the graph answers before anything moves',
    text: 'You tell Claude Code what you want in plain words: six, not five, for requirement R4. Nothing changes yet. The first thing it does is walk the links outward from R4 and report what hangs off it — the product page that shows the requirement, the product card that shows it too, and the buying flow that runs through it. That list is not inferred from the wording, and it is not somebody’s recollection of where things are. It is the links themselves, which is why it is complete. Then it stops and waits for your yes. This is the step that has no equivalent in a document: you are being told the size of the change while you can still decide not to make it.',
    watch: 'R4 in the middle, and the three nodes a change to it would reach. Nothing is marked yet — this is the graph answering a question, not carrying out an instruction.',
    alt: 'Step one: the impact of the change, before it is made',
  },
  {
    name: 'change-2.svg',
    title: 'The change lands, and everything leaning on it is told',
    text: 'R4 now says six. The three nodes that depend on it are marked needs review, and each carries the old wording beside the new, so a reviewer sees what actually moved instead of being told that something did. The visitor role is not marked, and that is worth a moment: U1 can add a product to the cart whether the limit is five or six, so the meaning of its link to R4 did not change, and marking it would be noise. Then Claude Code raises something you did not ask about. Rule B1 still says five, and R4 is supposed to follow B1 — the specification now contradicts itself, and it says so rather than letting you find out later.',
    watch: 'Three boxes turn amber, R4 turns green, and the visitor stays grey. The amber is not a warning about the change; it is a list of what has not been read yet.',
    alt: 'Step two: the change is made and dependent nodes are marked',
  },
  {
    name: 'change-3.svg',
    title: 'Every marked node is read again, by a person',
    text: 'You change B1 too, and the contradiction goes. Then the marked nodes have to be reviewed one at a time: the product page, the product card, the buying flow. Confirming one is deliberately not a button you can click through. The application prints a short code next to the new wording and asks for it back — a small mechanism with a large effect, because it means nobody can approve a node without having the new words in front of them. It is the one part of this that is not automated, and it is the part that should not be: a machine can tell you what a change touches, but only a person can say whether the new wording is right.',
    watch: 'The amber clears one box at a time as each is confirmed. By the end only the prototype is still outstanding.',
    alt: 'Step three: the marked nodes are reviewed and confirmed',
  },
  {
    name: 'change-4.svg',
    title: 'The prototype catches up',
    text: 'The prototype is built from the screens, so it goes stale the moment a screen does — and it is the thing people actually look at when they want to know what the product does, which makes a stale one worse than no prototype at all. The page is updated where it needs to be: the quantity field offers six now. It is checked and confirmed like everything else. That leaves one thing behind, and it is the big one — the product’s own code, written back when R4 said five. Nobody has told the developers. Nobody has to.',
    watch: 'The prototype turns green. The code is the last box still grey, and it is grey because nothing has rebuilt it yet.',
    alt: 'Step four: the prototype is updated',
  },
  {
    name: 'change-5.svg',
    title: 'The code catches up, and the trail is kept',
    text: 'A builder agent opens by asking the specification one question: what has changed since the version I last built from? It gets back R4, B1 and the nodes that depend on them — not the whole specification, and not a list of files to re-read. It rebuilds that much, writes the tests from the acceptance criteria as they now stand, names each test after the criterion it came from, and records the version it built against so the next question has an answer. What is left behind is the trail: who changed the number, when, why, what it touched, and who read it. In six months, when somebody asks why the limit is six, the answer is in the specification rather than in whoever happens to remember.',
    watch: 'Everything is green. The same five boxes you started with, in the same places — which is the point of the sequence: nothing moved, the state travelled.',
    alt: 'Step five: the code is rebuilt from the new specification',
  },
];

const faq: [string, string][] = [
  [
    'Do I need to be a developer to use it?',
    'No. You talk to Claude Code in plain words. You install Python and Claude Code once, and the public repository has a getting-started guide written for people who have never opened a terminal.',
  ],
  [
    'Where is my data kept?',
    'On your computer, as plain text files in your project folder. The application that shows them runs on your computer too, and the files can live in Git like any other source. Claude Code itself sends your conversation to Anthropic to answer you.',
  ],
  [
    'What if the AI writes something wrong?',
    'Every requirement records where it came from and how sure the specification is about it. Nothing is final until you agree it, and the tool will not let you agree while questions are still open. Every change is logged, with who made it and why.',
  ],
  [
    'Which agents can build from it?',
    'Any coding agent that can run a command. The folder carries an AGENTS.md that many agents read by themselves, a CLAUDE.md that points Claude Code at it, and a build guide. The agent does not need the skill, and the product can be written in any language.',
  ],
  [
    'Can an agent change the specification by itself?',
    'A builder agent does not. Its guide tells it to read only, and to write anything unclear into an inbox for the person who keeps the specification. Changes go through the skill, when a person asks, and each one is checked and logged.',
  ],
  [
    'Does it replace Jira or Confluence?',
    'No. Keep your tracker for planning and tracking the work. What the graph replaces is the requirements that get copied into those tools, so there is one place to link to instead of four to reconcile.',
  ],
  [
    'Does it work for a product that already exists?',
    'Yes. It can read an existing codebase, website or set of documents and write the specification from them, and each requirement then names the place it was read from. The Voltline example was written that way.',
  ],
  [
    'How big can a specification be?',
    'Voltline has 541 nodes. The application stays fast well beyond that — it has been tested at 54,000.',
  ],
  [
    'What does it cost?',
    'specs-builder is free and open source under the MIT licence. Writing a specification needs Claude Code on a paid Claude plan. Reading one needs only Python and a browser.',
  ],
];

export default function ArticlePart() {
  return (
    <>
      <ContentsPart />

      {/* The article's premise, said in two lines before anything else. The
          site's blockquote recipe sets it off with a rule and italics, which
          is the right weight for an epigraph. */}
      <blockquote className="text-ink">
        A document is a container of information.
        <br />A specification is a structured representation of a problem.
      </blockquote>

      <p className="text-ink">
        They are not the same kind of thing, and keeping the second inside the first is where the
        trouble starts. A specification is one problem looked at from several sides at once — what
        the product must do, the rules it follows, the people who use it, the screens that show it,
        a prototype you can click, the code and the tests built from all of that. Every side is
        describing the same thing. Every side keeps its own copy of the facts.
      </p>

      <p>
        And the sides are not joined to each other. The requirements document does not know which
        screen shows which requirement. The prototype does not know which rule it is obeying. The
        tests know a name and nothing else. Each one is written on its own and read on its own, so
        following a single fact across them means knowing, from memory, where its copies are — and
        nothing will tell you when your memory is wrong. It looks like this:
      </p>

      <SidesPart />

      <p>To see why that matters, start with how it goes today.</p>

      <ScenarioPart
        beats={[
          {
            text: (
              <>
                A team has its specification in exactly those six places, and the rule above sits in
                all of them: a cart holds up to five of one product. It has been true for a year.
                Nobody has had to think about where it is written down.
              </>
            ),
          },
          {
            when: 'The change',
            text: (
              <>
                The product manager changes it. Five becomes six, typed into the requirement that
                says so, and the decision is made. Ten seconds. Every other copy of that fact now
                has to be found and changed by hand — and nothing anywhere knows how many there are,
                or where.
              </>
            ),
          },
          {
            when: 'Two weeks later',
            text: (
              <>
                The product page still stops at five. A test still expects five. The help article
                says five. And an agent, asked that morning for a bulk-order screen, read the
                requirement, found five, and built five — correctly, from what it was given, in
                about four minutes.
              </>
            ),
          },
        ]}
      >
        Nobody did anything wrong. Nobody skipped a step or missed a meeting. The fact was written
        down in five places, the person who changed it could see one, and nothing in the toolchain
        was able to say which four were left behind.
      </ScenarioPart>

      <SectionPart title={SECTIONS.problem} />

      <p>
        A team writes its requirements in a document. Then the same facts are copied into tickets,
        designs, code and tests. Every copy is made by hand.
      </p>

      <p>
        Go back to the change at the top: a cart could hold five, and now it can hold six. Someone
        edits the document. But who updates the ticket, the design, the code and the tests? Usually
        nobody knows all the places. Some copies still say five, and nobody is warned.
      </p>

      <FigurePart name="drift.svg" alt="One rule written in five places, only one of them updated">
        One rule, five places. The change reaches the place someone edited. The others still say
        five.
      </FigurePart>

      <p>
        The real cost is not the edit. It is the search for every place, and the mistakes that come
        from the places that were missed. A tester finds the product page still stops at five. A
        developer asks which number is right. A meeting goes on a fact that was settled weeks ago.
      </p>

      <p>
        Coding agents make this worse, not better. They build fast, but only from what they are
        given. Give them a specification that is out of date and they will build the wrong thing,
        quickly.
      </p>

      <SectionPart title={SECTIONS.solution} />

      {/* The thesis, in the same accent panel the key idea gets at the far end
          of the article — the claim and the proof of it, dressed alike. One
          step up in size from the body, which is as much as the scale allows
          without reaching for a title. */}
      <p className="border-accent-line bg-accent-soft/60 text-ink text-card my-8 rounded-xl border p-5 sm:p-6">
        This article is about another way to hold a specification. Instead of pages of prose, it is
        a <strong>graph</strong>: many small facts, each written once, each linked to the facts that
        depend on it. You write it by talking to an AI assistant in plain words. People read it in a
        browser. Agents build the product from it. And before anyone changes a single fact, the
        graph shows <strong>everything that change will touch</strong>.
      </p>

      <p>
        Nothing below is a mock-up. Every picture comes from a working example you can open on your
        own machine in a few minutes, and the tool is free and open source.
      </p>

      <FigurePart
        name="around.png"
        alt="One requirement in the graph, with the rule, roles, screens and evidence linked to it"
      >
        One requirement from a real example, with everything linked to it. Each box is one small
        fact; each line is a link with a meaning.
      </FigurePart>

      <MarksPart
        items={[
          <>
            <strong>R4</strong>, a requirement: a visitor or a customer can add a product to the
            cart.
          </>,
          <>
            <strong>B1</strong>, the rule it follows: a cart holds up to five of one product.
          </>,
          <>
            <strong>SC3</strong>, a screen that shows it: the product page.
          </>,
          <>
            <strong>U2</strong>, a role that can do it: the customer.
          </>,
          <>
            <strong>E14</strong>, the evidence: where the requirement was found.
          </>,
          <>
            <strong>Q1</strong>, a question about it that is still open.
          </>,
        ]}
      />

      <CardsPart
        cards={[
          {
            kicker: 'Safer changes',
            title: 'See the impact first',
            body: 'Before you change a rule, you see every requirement, screen and test that depends on it.',
          },
          {
            kicker: 'One truth',
            title: 'One source for people and agents',
            body: 'People read the specification in a browser. Agents build the product from the same files.',
          },
          {
            kicker: 'Full history',
            title: 'Nothing gets lost',
            body: 'Every requirement says where it came from. Every open question stays visible until someone answers it.',
          },
        ]}
      />

      <SectionPart title={SECTIONS.idea} />

      <p>
        Instead of long pages of text, the specification is a <strong>graph</strong> — a set of
        small facts, called <strong>nodes</strong>, joined by <strong>links</strong>. Each fact is
        written once. Each link says how two facts depend on each other: a screen <em>shows</em> a
        requirement, a requirement <em>follows</em> a rule.
      </p>

      <FigurePart
        name="idea.svg"
        alt="The same rule on four unconnected pages, beside the same rule written once with everything pointing to it"
      >
        On the left, the same rule appears on four pages and nothing connects them. On the right it
        is written once, and everything that depends on it points at it.
      </FigurePart>

      <p>
        Because the links are stored rather than implied, a computer can follow them. Change rule
        B1, and the graph knows exactly which requirements, screens and components depend on it. You
        do not have to search, and you do not have to remember.
      </p>

      <p>
        A link reads like a short sentence: <em>SC3 shows R4</em>, <em>R4 follows B1</em>. There are
        about twenty kinds of node — goals, requirements, rules, roles, screens, components, API
        endpoints, open questions — and the letters of an ID tell you the kind: R is a requirement,
        B a rule, SC a screen. Nobody draws the graph by hand. It is in the files, and every picture
        of it is made from them.
      </p>

      <h3>Words you will see</h3>

      <TablePart
        header={['Word', 'What it means']}
        rows={[
          ['Node', 'One small fact: a requirement, a rule, a screen, a question.'],
          [
            'Link',
            <>
              A connection with a meaning, such as <em>shows</em> or <em>follows</em>.
            </>,
          ],
          ['ID', 'A short name for a node, such as R4 or SC3. Every node has one.'],
          ['Requirement', 'Something the product must do, with its reason and its tests.'],
          ['Acceptance criterion', 'A test in plain words: given this, when that, then this.'],
          [
            'Needs review',
            <>
              A node that depends on something that has changed. The application calls it{' '}
              <em>stale</em>.
            </>,
          ],
          [
            'Flow',
            'The steps a user takes to reach a goal, such as buying a product, and the screens on the way.',
          ],
          [
            'Prototype',
            'A page that looks and works like the real screen, made before the real product is built.',
          ],
          ['Design system', 'The colours, fonts and spacing that every screen uses.'],
          [
            'Skill',
            'A set of instructions and tools that Claude Code loads when it needs them. specs-builder is one.',
          ],
          [
            'Application',
            'The program that comes inside every specification and shows it in a browser.',
          ],
          [
            'Builder agent',
            'An agent, such as Claude Code, whose job is to write the product’s code and tests.',
          ],
        ]}
      />

      <SectionPart title={SECTIONS.parts} />

      <p>
        specs-builder is not one program. It is three parts, and each is used by someone different.
        Once the three are clear, the rest of this follows easily.
      </p>

      <FigurePart
        name="parts.svg"
        alt="The skill produces the application, which has one interface for people and one for agents"
      >
        You talk to the skill. The skill produces the application. The application has one interface
        for people and one for the agents that build the product.
      </FigurePart>

      <p>
        <strong>1. The skill is what you talk to.</strong> It runs inside Claude Code, Anthropic’s
        assistant for the terminal and the editor. The skill teaches it how to write a
        specification: what to ask, what to write, and how to check it. You talk in plain words. It
        can also read an existing codebase, website or pile of documents and write the specification
        from them. You never edit the files yourself — the skill makes every change, and checks the
        whole specification before it saves one.
      </p>

      <p>
        <strong>2. The application is what the skill produces.</strong> A specification is one
        folder in your project. It holds the facts as plain text, one file per node, and a small
        application that travels with them. It needs only Python, runs on your machine, and opens in
        your browser. Because it lives inside the folder, anyone who receives the folder can read
        the specification, with or without the skill.
      </p>

      <p>
        <strong>3. The application has two interfaces.</strong> The same facts, offered two ways,
        one for each kind of reader. Nothing is copied between them, so people and agents can never
        be looking at different versions.
      </p>

      <CardsPart
        cols={2}
        cards={[
          {
            kicker: 'Interface for people',
            title: 'Pages in a browser',
            body: 'The document, the graph, the layers, the matrix and a working prototype. People read and explore but do not edit; a button on every page sends a change request to whoever keeps the specification. The whole thing can also be saved as a single HTML file and sent to anyone.',
          },
          {
            kicker: 'Interface for builder agents',
            title: 'A guide and commands',
            body: 'An AGENTS.md that coding agents read by themselves, a step-by-step build guide, and commands that give exact answers, as JSON when that is what is wanted. An agent asks what to build first, what each part needs, which tests to write, and what has changed since its last build.',
          },
        ]}
      />

      <p>
        A <strong>builder agent</strong> is an agent whose job is to write the product’s code and
        tests. It does not need the skill: everything it needs is in the folder. So one person can
        write the specification and an agent somewhere else can build from it, in any language. The
        agent never changes the specification. When something is unclear it writes a question into
        an inbox, and a person answers it.
      </p>

      <SectionPart title={SECTIONS.tour} />

      <p>
        These are screens from <strong>Voltline</strong>, a made-up electronics shop that ships with
        the tool as an example. Its specification has 541 nodes and 1,898 links; the graph view
        shows the 201 main ones, the rest being small parts inside them, such as the fields of a
        screen. Click any picture to open it full size.
      </p>

      <GalleryPart shots={shots} />

      <SectionPart title={SECTIONS.how} />

      <p>There are four steps, and you only do the first one yourself.</p>

      <FigurePart
        name="overview.svg"
        alt="You talk, Claude Code writes, people read, agents build, and changes come back to the start"
      >
        You talk. Claude Code writes. People read. Agents build. When someone wants a change, it
        comes back to the start.
      </FigurePart>

      <p>
        The specification is saved as plain text files in your project, so you own it. It can sit in
        Git next to the code it describes, with the same history and the same review.
      </p>

      <h3>1. You talk, Claude Code asks</h3>

      <p>
        You start with one sentence. Claude Code writes down what the sentence already says, then
        asks only what it cannot know: who signs in, what a word means, what is out of scope. Before
        it draws any screen it asks how the product should look. Every answer becomes a node with an
        ID, and every open question stays visible until someone answers it.
      </p>

      <p>
        There are three ways in, and you can switch between them at any time. You write, and the
        skill completes what you wrote and asks about the rest. The skill asks, and writes from your
        answers. Or you point it at something that already exists — code, a website, documents — and
        it writes what it finds, recording where it found each fact.
      </p>

      <p>
        It also adds the cases you did not mention, such as what happens when the cart is empty, and
        marks each one <em>added</em> until you confirm it. What it will not do is guess a fact
        about the world: a price, a number, what users do, what the law says. Those are asked, and
        they stay open questions until someone answers them.
      </p>

      <FigurePart name="talked.svg" alt="A short example conversation with the skill">
        A short example conversation. Between the messages the tool checks its own work: every link
        points at a real node, and nothing contradicts anything else.
      </FigurePart>

      <h3>2. What the graph holds</h3>

      <p>
        A specification holds a good deal more than requirements. It has six parts, and every part
        is linked to the requirements it serves.
      </p>

      <ul>
        <li>
          <strong>Goals and requirements</strong>: why the product exists and what it must do, each
          requirement with its tests.
        </li>
        <li>
          <strong>The domain</strong>: the words of the business, the things it keeps — a cart, an
          order — its rules and its roles.
        </li>
        <li>
          <strong>The user experience</strong>: the flows, the screens on them, and the components
          the screens are made of.
        </li>
        <li>
          <strong>The look</strong>: the design system, and a working prototype of every screen.
        </li>
        <li>
          <strong>The API</strong>: the endpoints other programs call, where the product has them.
        </li>
        <li>
          <strong>The history</strong>: open questions, decisions with what was turned down, and the
          evidence behind each fact.
        </li>
      </ul>

      <FigurePart name="graph.svg" alt="The kinds of node in one specification and how they link">
        The kinds of node in one specification, and how they link. Requirements in the centre; on
        the left why they exist, on the right how they are shown and built.
      </FigurePart>

      <h3>3. People read it, agents build from it</h3>

      <p>
        This is where the two interfaces earn their keep. People open the specification in a
        browser, read the document, walk the graph, click through the prototype — or share the whole
        thing as one HTML file that needs nothing installed. Builder agents read the same files
        through commands: they ask questions, get exact answers, and ask what has changed since
        their last build.
      </p>

      <FigurePart name="readers.svg" alt="One source read by both people and agents">
        One source, two kinds of reader. Nothing is made for the agents that people cannot also see.
      </FigurePart>

      <p>
        A builder agent follows a fixed procedure, written in the folder. First it checks that
        nothing has changed without review. It reads the overview, then asks for a plan: the parts
        to build, in order. For each part, one command gives everything that part needs. It writes
        the tests first, from the acceptance criteria, and names each test after the criterion —
        R4.1 — so every test traces back to the requirement it came from. When the build is done and
        you agree it, the agent records which version of the specification it built from. Next time
        it asks what has changed since then, and rebuilds only that.
      </p>

      <SectionPart title={SECTIONS.change} />

      <p>
        This is the part that matters, and the reason a specification is worth holding as a graph at
        all. Everything above is arrangement; this is what the arrangement is for.
      </p>

      <p>
        Here is the change from the top of this article, followed all the way through: a cart can
        now hold <strong>six</strong> of a product, not five. The same ten-second edit, in the same
        product, with the same six places holding a copy of the rule. What is different is that the
        copies are now linked to the thing they came from, and a link is something a computer can
        follow.
      </p>

      <p>
        It runs in five steps, and only the first and third need a person. Before any of them, the
        application will show you what you are about to be let in for.
      </p>

      <FigurePart
        name="impact.png"
        alt="The application showing the six nodes that depend on rule B1"
      >
        Before anything changes, the application shows what a change to rule B1 would touch.
      </FigurePart>

      <MarksPart
        items={[
          <>
            <strong>B1</strong>, the rule you want to change: up to five of a product.
          </>,
          <>
            The six nodes that depend on it: requirements, the cart, a component, a screen and an
            endpoint.
          </>,
          <>How many more depend on each of those, one step further out.</>,
          <>The count, so you know the size of the change before you start.</>,
        ]}
      />

      <StepsPart steps={steps} />

      <p>
        How does the graph know what to mark? Not by reading. Each link remembers the version of
        the node it points at, as of the last time somebody reviewed that link. When the node
        changes, its version moves on, the two no longer match, and the node at the other end of
        the link is marked <em>needs review</em>. That is the whole mechanism — a comparison of two
        numbers, per link.
      </p>

      <p>
        Being that dumb is the point. Nothing is inferred from the wording, so it cannot miss a
        dependency because the rule was phrased differently in two places — the failure that made
        the six tiles at the top of this article impossible to search. And it cannot over-report
        either: a node whose link did not change is not marked, so the review list is short enough
        that people actually work through it. A list that cries wolf gets approved in bulk, and
        then it is worth nothing.
      </p>

      <p>
        What a reviewer sees is not a notification saying something changed somewhere. It is the
        node itself, with the old words struck out and the new ones beside them:
      </p>

      <FigurePart
        name="stale-node.png"
        alt="One element of the product page marked as needing review, with the words that changed"
      >
        What a reviewer sees in the application after the change.
      </FigurePart>

      <MarksPart
        items={[
          <>The element: the quantity field on the product page. It is one node in the graph.</>,
          <>The warning: two facts it depends on have changed since it was last reviewed.</>,
          <>
            The exact words that changed: <em>five</em> struck out, <em>six</em> new.
          </>,
          <>
            How to confirm it after reading — the code at the end proves the latest words were read.
          </>,
          <>Its own text still says 1 to 5. That is exactly what the review is there to catch.</>,
        ]}
      />

      <KeyIdeaPart>
        People change the specification, not the code. The graph shows what each change touches.
        Agents carry the change into the code. A product owner never has to read code to know what a
        change means.
      </KeyIdeaPart>

      <SectionPart title={SECTIONS.roles} />

      <CardsPart
        cards={[
          {
            kicker: 'Product owner',
            title: 'Control without reading code',
            body: 'You describe the product in your own words, and you see what each change will touch before you approve it. Nothing is built from a version you did not agree.',
          },
          {
            kicker: 'Developer',
            title: 'Clear answers, not guesses',
            body: 'Every requirement has its reason, its tests in plain words, and links to the screens and endpoints that serve it. Where something is unclear there is an open question, not a silent assumption.',
          },
          {
            kicker: 'Tester',
            title: 'Tests that come from the specification',
            body: 'Each requirement carries acceptance criteria written as given, when, then. When a requirement changes, you see which tests have gone out of date.',
          },
          {
            kicker: 'Manager',
            title: 'One view of the whole product',
            body: 'One place shows what is agreed, what is still open, and what a change would cost. The history shows who decided what, and why.',
          },
          {
            kicker: 'Builder agent',
            title: 'Exact context, not a long document',
            body: 'Agents ask the specification questions and get exact answers, and build only what has changed since their last build.',
          },
        ]}
      />

      <SectionPart title={SECTIONS.compare} />

      <TablePart
        header={['', 'Documents', 'Tickets', 'Design files', 'Specifications as a graph']}
        rows={[
          [
            <strong>Each fact is written</strong>,
            'Many times',
            'Many times',
            'Many times',
            <strong>Once</strong>,
          ],
          [
            <strong>Links between facts</strong>,
            'In the text only',
            'Some, by hand',
            'None',
            <strong>Every fact, with a meaning</strong>,
          ],
          [
            <strong>What a change touches</strong>,
            'You search and hope',
            'Partly, by hand',
            'Not shown',
            <strong>Shown before the change</strong>,
          ],
          [
            <strong>Where a requirement came from</strong>,
            'Sometimes',
            'Sometimes',
            'No',
            <strong>Always, with its evidence</strong>,
          ],
          [
            <strong>Open questions</strong>,
            'Lost in comments',
            'In comments',
            'In comments',
            <strong>Visible until answered</strong>,
          ],
          [
            <strong>Agents can use it exactly</strong>,
            'Only as text',
            'Partly',
            'No',
            <strong>Yes, through commands</strong>,
          ],
          [
            <strong>Format</strong>,
            'Word or wiki pages',
            'A tracker’s database',
            'A design tool’s file',
            <strong>Plain text files in Git</strong>,
          ],
        ]}
        caption="Documents means Word or Confluence, tickets means Jira, design files means Figma. The graph does not replace a task tracker; it replaces the requirements that get copied into one."
      />

      <SectionPart title={SECTIONS.questions} />

      <FaqPart items={faq} />

      <SectionPart title={SECTIONS.try} />

      <p>
        The tool is free and open source. You can open the finished Voltline example in a few
        minutes without writing anything. You need Python 3.14 or later, and Git.
      </p>

      <pre className="bg-chip text-ink">
        <code>
          {`git clone https://github.com/vasilegrafu/project.specs-builder.git
cd project.specs-builder
sh open-example.sh        # on Windows: open-example.cmd`}
        </code>
      </pre>

      <p>
        Then start Claude Code in the same folder and say:{' '}
        <em>
          use specs-builder to write a spec for a portal where customers download their invoices
        </em>
        . The full guide is in the{' '}
        <a href="https://github.com/vasilegrafu/project.specs-builder">repository on GitHub</a>.
      </p>
    </>
  );
}
