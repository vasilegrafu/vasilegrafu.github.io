# LinkedIn article — Specifications as a graph

Paste-ready, and the same as the published article:
`https://www.linkedin.com/pulse/specifications-graph-vasile-grafu-5lh9f/`

It is a cut of the site article
(`https://vasilegrafu.github.io/articles/specifications-as-a-graph`): shorter,
with ten pictures, and pointing at the site for the rest. When the published
article changes, change this file to match, so the two cannot drift.

**LinkedIn's editor does not understand Markdown.** Pasting `## Heading` gives
you a literal `##`. So nothing below uses Markdown syntax: headings are given
as plain lines you paste and then style with the editor's own H2 button, and
every fenced block is text to paste verbatim.

**How to use this file.** Work top to bottom. For each section: paste the
heading line and press H2, paste the body block, then insert the picture named
in the `[IMAGE nn]` marker and type its caption underneath. Ten pictures, in
the order they appear here, are in `images/`.

---

## Before you paste

**Title** _(LinkedIn shows about 100 characters in the feed)_

```
Specifications as a graph
```

**Subtitle** — LinkedIn has no subtitle field for articles. The first
paragraph does that job, which is why the opening below is the definition.

**Cover image**: `cover.png` (1920×1080). Built from the application's own
screens: the title on the left, the graph and two of its screens fanned off the
right edge. That is the size LinkedIn's help gives as optimal for an article
cover — 16:9, centred — so nothing is cropped away.

---

## 1. Opening

Paste as a quote block (the editor's `"` button):

```
A document is a container of information. A specification is a structured representation of a problem.
```

Then the body:

```
They are not the same kind of thing, and keeping the specification inside a document is where the trouble starts. A specification is one problem looked at from several sides at once — what the product must do, the rules it follows, the people who use it, the screens that show it, a prototype you can click, the code and the tests built from all of that. Every side is describing the same thing. Every side keeps its own copy of the facts.

And the sides are not joined to each other. The requirements document does not know which screen shows which requirement. The prototype does not know which rule it is obeying. The tests know a name and nothing else. Each one is written on its own and read on its own, so following a single fact across them means knowing, from memory, where its copies are — and nothing will tell you when your memory is wrong.
```

---

## 2. A scenario

Heading (apply H2):

```
A scenario
```

Body — the six lines are a bulleted list (the editor's list button):

```
One rule, six places, six wordings, and not one line between them:

• The requirements document — “a cart holds up to five of a product”
• A page in the wiki — “max 5 per line”
• The design file — a quantity field, 1–5
• The prototype — a dropdown, 1 to 5
• The tracker — “limit 5” in a ticket
• The code and its tests — MAX_PER_LINE = 5

Nothing there points at anything else there. To see why that matters, start with how it goes today.

A team has its specification in exactly those six places, and the rule above sits in all of them: a cart holds up to five of one product. It has been true for a year. Nobody has had to think about where it is written down.

Now the change. The product manager changes it. Five becomes six, typed into the requirement that says so, and the decision is made. Every other copy of that fact now has to be found and changed by hand — and nothing anywhere knows how many there are, or where. Two weeks later. The product page still stops at five. A test still expects five. The help article says five. And an agent, asked that morning for a bulk-order screen, read the requirement, found five, and built five — correctly, from what it was given, in about four minutes.

• Nobody did anything wrong.
• Nobody skipped a step or missed a meeting.
• The fact was written down in five places, the person who changed it could see one, and nothing in the toolchain was able to say which four were left behind.
```

---

## 3. The problem today

Heading (apply H2):

```
The problem today
```

Body:

```
Go back to the change at the top: a cart could hold five, and now it can hold six. Someone edits the document. But who updates the ticket, the design, the code and the tests? Usually nobody knows all the places. Some copies still say five, and nobody is warned.
```

`[IMAGE 01 — images/01-the-problem-one-rule-five-places.png]`

Caption:

```
One rule, five places. The change reaches the place someone edited. The others still say five.
```

Body:

```
The real cost is not the edit. It is the search for every place, and the mistakes that come from the places that were missed. A tester finds the product page still stops at five. A developer asks which number is right. A meeting goes on a fact that was settled weeks ago. Coding agents make this worse, not better. They build fast, but only from what they are given. Give them a specification that is out of date and they will build the wrong thing, quickly.
```

---

## 4. A solution: specifications as a graph

Heading (apply H2):

```
A solution: specifications as a graph
```

Body:

```
This article is about another way to hold a specification. Instead of pages of prose, it is a graph: many small facts, each written once, each linked to the facts that depend on it.

You write it by talking to an AI assistant in plain words. People read it in a browser. Agents build the product from it. And before anyone changes a single fact, the graph shows everything that change will touch. Nothing below is a mock-up. Every picture comes from a working example you can open on your own machine in a few minutes, and the tool is free and open source.
```

`[IMAGE 02 — images/02-the-layers.png]` — no caption.

`[IMAGE 03 — images/03-a-requirement-and-its-links.png]` — no caption.

---

## 5. The idea: small facts, linked

Heading (apply H2):

```
The idea: small facts, linked
```

Body:

```
Instead of long pages of text, the specification is a graph — a set of small facts, called nodes, joined by links. Each fact is written once. Each link says how two facts depend on each other: a screen shows a requirement, a requirement follows a rule.
```

`[IMAGE 04 — images/04-document-versus-graph.png]`

Caption:

```
On the left, the same rule appears on four pages and nothing connects them. On the right it is written once, and everything that depends on it points at it.
```

Body:

```
Because the links are stored rather than implied, a computer can follow them. Change rule B1, and the graph knows exactly which requirements, screens and components depend on it. You do not have to search, and you do not have to remember.

A link reads like a short sentence: SC3 shows R4, R4 follows B1. There are about twenty kinds of node — goals, requirements, rules, roles, screens, components, API endpoints, open questions — and the letters of an ID tell you the kind: R is a requirement, B a rule, SC a screen. Nobody draws the graph by hand. It is in the files, and every picture of it is made from them.
```

---

## 6. See it working

Heading (apply H2):

```
See it working
```

Body:

```
These are screens from Voltline, a made-up electronics shop that ships with the tool as an example. Its specification has 541 nodes and 1,898 links; the graph view shows the 201 main ones, the rest being small parts inside them, such as the fields of a screen.
```

`[IMAGE 05 — images/05-the-whole-specification.png]`

Caption:

```
The whole specification. Each bubble is one kind of node, sized by how many there are. Each line shows how many links join two kinds.
```

`[IMAGE 06 — images/06-one-requirement.png]`

Caption:

```
One requirement, R4 in full: what it says, where it came from, how sure the specification is, and the question still open about it.
```

`[IMAGE 07 — images/07-a-working-prototype.png]`

Caption:

```
A working prototype: a real page, built from the screen's description and the design system. Viewable at phone, tablet or desktop size.
```

Body:

```
There are nine more views — the layers, one flow through the layers, the acceptance criteria, the design system, every element of a screen labelled with the requirement it serves, and a matrix of what links to what. They are all in the full article, linked at the end.
```

---

## 7. How it works

Heading (apply H2):

```
How it works
```

Body:

```
There are four steps, and you only do the first one yourself.
```

`[IMAGE 08 — images/08-how-it-works.png]`

Caption:

```
You talk. Claude Code writes. People read. Agents build. When someone wants a change, it comes back to the start.
```

Body — the six lines under "2)" are a bulleted list:

```
The specification is saved as plain text files in your project, so you own it. It can sit in Git next to the code it describes, with the same history and the same review.

1) You talk, Claude Code asks. You start with one sentence. Claude Code writes down what the sentence already says, then asks only what it cannot know: who signs in, what a word means, what is out of scope. Every answer becomes a node with an ID, and every open question stays visible until someone answers it.

There are three ways in, and you can switch between them at any time. You write, and the skill completes what you wrote and asks about the rest. The skill asks, and writes from your answers. Or you point it at something that already exists — code, a website, documents — and it writes what it finds, recording where it found each fact.

It also adds the cases you did not mention, such as what happens when the cart is empty, and marks each one added until you confirm it. What it will not do is guess a fact about the world: a price, a number, what users do, what the law says. Those are asked, and they stay open questions until someone answers them.

2) What the graph holds. A specification holds a good deal more than requirements. It has six parts, and every part is linked to the requirements it serves.

• Goals and requirements: why the product exists and what it must do, each requirement with its tests.
• The domain: the words of the business, the things it keeps — a cart, an order — its rules and its roles.
• The user experience: the flows, the screens on them, and the components the screens are made of.
• The look: the design system, and a working prototype of every screen.
• The API: the endpoints other programs call, where the product has them.
• The history: open questions, decisions with what was turned down, and the evidence behind each fact.
```

`[IMAGE 09 — images/09-kinds-of-node.png]`

Caption:

```
The kinds of node in one specification, and how they link. Requirements in the centre; on the left why they exist, on the right how they are shown and built.
```

Body:

```
3) People read it, agents build from it. This is where the two interfaces earn their keep. People open the specification in a browser, read the document, walk the graph, click through the prototype — or share the whole thing as one HTML file that needs nothing installed. Builder agents read the same files through commands: they ask questions, get exact answers, and ask what has changed since their last build.
```

`[IMAGE 10 — images/10-one-source-two-readers.png]`

Caption:

```
One source, two kinds of reader. Nothing is made for the agents that people cannot also see.
```

Body:

```
A builder agent follows a fixed procedure, written in the folder. First it checks that nothing has changed without review. It reads the overview, then asks for a plan: the parts to build, in order. For each part, one command gives everything that part needs. It writes the tests first, from the acceptance criteria, and names each test after the criterion — R4.1 — so every test traces back to the requirement it came from. When the build is done and you agree it, the agent records which version of the specification it built from. Next time it asks what has changed since then, and rebuilds only that.

The key idea: people change the specification, not the code. The graph shows what each change touches. Agents carry the change into the code. A product owner never has to read code to know what a change means.
```

---

## 8. What each role gets

Heading (apply H2):

```
What each role gets
```

Body:

```
Product owner — control without reading code. You describe the product in your own words, and you see what each change will touch before you approve it. Nothing is built from a version you did not agree.

Developer — clear answers, not guesses. Every requirement has its reason, its tests in plain words, and links to the screens and endpoints that serve it. Where something is unclear there is an open question, not a silent assumption.

Tester — tests that come from the specification. Each requirement carries acceptance criteria written as given, when, then. When a requirement changes, you see which tests have gone out of date.

Manager — one view of the whole product. One place shows what is agreed, what is still open, and what a change would cost. The history shows who decided what, and why.

Builder agent — exact context, not a long document. Agents ask the specification questions and get exact answers, and build only what has changed since their last build.
```

---

## 9. Try it

Heading (apply H2):

```
Try it
```

Body:

```
The tool is free and open source. You can open the finished Voltline example in a few minutes without writing anything. You need Python 3.14 or later, and Git.
```

Paste as a code block (the editor's `</>` button):

```
git clone https://github.com/vasilegrafu/project.specs-builder.git
cd project.specs-builder
sh open-example.sh        # on Windows: open-example.cmd
```

Body:

```
Then start Claude Code in the same folder and say: use specs-builder to write a spec for a portal where customers download their invoices. The full guide is in the repository on GitHub.

The long version of this article, with all fifteen screenshots at full size and every diagram, is on my site: https://vasilegrafu.github.io/articles/specifications-as-a-graph
```

---

## Afterwards

- Set the article's tags to three of: AI-assisted development, product specification, agentic architectures, requirements engineering, product management.
- Publish, then post the feed post in `../post/post.md` with the article's link.
