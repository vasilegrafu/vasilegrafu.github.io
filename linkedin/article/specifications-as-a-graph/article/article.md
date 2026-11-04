# LinkedIn article — Specifications as a graph

Paste-ready. Source: `https://vasilegrafu.github.io/articles/specifications-as-a-graph`
(the site article at the commit this file was written). Regenerate rather than
hand-edit, so LinkedIn and the site cannot drift.

**LinkedIn's editor does not understand Markdown.** Pasting `## Heading` gives
you a literal `##`. So nothing below uses Markdown syntax: headings are given
as plain lines you paste and then style with the editor's own H2 button, and
every fenced block is text to paste verbatim.

**How to use this file.** Work top to bottom. For each section: paste the
heading line and press H2, paste the body block, then insert the picture named
in the `[IMAGE nn]` marker and type its caption underneath. Seventeen pictures,
in the order they appear here, are in `images/`.

---

## Before you paste

**Title** _(LinkedIn shows about 100 characters in the feed)_

```
Specifications as a graph
```

**Subtitle** — LinkedIn has no subtitle field for articles. The first
paragraph does that job, which is why the opening below is the definition.

**Cover image**: `cover.png` (1920×1080). LinkedIn crops the cover to a wide
strip on some surfaces, so the picture sits centred with room around it.

---

## 1. Opening

Paste as a quote block (the editor's `"` button):

```
A document is a container of information. A specification is a structured representation of a problem.
```

Then the body:

```
They are not the same kind of thing, and keeping the second inside the first is where the trouble starts. A specification is one problem looked at from several sides at once — what the product must do, the rules it follows, the people who use it, the screens that show it, a prototype you can click, the code and the tests built from all of that. Every side is describing the same thing. Every side keeps its own copy of the facts.

And the sides are not joined to each other. The requirements document does not know which screen shows which requirement. The prototype does not know which rule it is obeying. The tests know a name and nothing else. Each one is written on its own and read on its own, so following a single fact across them means knowing, from memory, where its copies are — and nothing will tell you when your memory is wrong.

One rule, six places, six wordings, and not one line between them:

• The requirements document — “a cart holds up to five of a product”
• A page in the wiki — “max 5 per line”
• The design file — a quantity field, 1–5
• The prototype — a dropdown, 1 to 5
• The tracker — “limit 5” in a ticket
• The code and its tests — MAX_PER_LINE = 5

Nothing there points at anything else there. To see why that matters, start with how it goes today.
```

---

## 2. A scenario

Heading (apply H2):

```
A scenario
```

Body:

```
A team has its specification in exactly those six places, and the rule above sits in all of them: a cart holds up to five of one product. It has been true for a year. Nobody has had to think about where it is written down.

The change. The product manager changes it. Five becomes six, typed into the requirement that says so, and the decision is made. Every other copy of that fact now has to be found and changed by hand — and nothing anywhere knows how many there are, or where.

Two weeks later. The product page still stops at five. A test still expects five. The help article says five. And an agent, asked that morning for a bulk-order screen, read the requirement, found five, and built five — correctly, from what it was given, in about four minutes.

Nobody did anything wrong. Nobody skipped a step or missed a meeting. The fact was written down in five places, the person who changed it could see one, and nothing in the toolchain was able to say which four were left behind.
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
The real cost is not the edit. It is the search for every place, and the mistakes that come from the places that were missed. A tester finds the product page still stops at five. A developer asks which number is right. A meeting goes on a fact that was settled weeks ago.

Coding agents make this worse, not better. They build fast, but only from what they are given. Give them a specification that is out of date and they will build the wrong thing, quickly.
```

---

## 4. A solution: specifications as a graph

Heading (apply H2):

```
A solution: specifications as a graph
```

Body:

```
This article is about another way to hold a specification. Instead of pages of prose, it is a graph: many small facts, each written once, each linked to the facts that depend on it. You write it by talking to an AI assistant in plain words. People read it in a browser. Agents build the product from it. And before anyone changes a single fact, the graph shows everything that change will touch.

Nothing below is a mock-up. Every picture comes from a working example you can open on your own machine in a few minutes, and the tool is free and open source.
```

`[IMAGE 02 — images/02-a-requirement-and-its-links.png]`

Caption:

```
One requirement from a real example, with everything linked to it. Each box is one small fact; each line is a link with a meaning.
```

Body:

```
What you are looking at:

• R4, a requirement: a visitor or a customer can add a product to the cart.
• B1, the rule it follows: a cart holds up to five of one product.
• SC3, a screen that shows it: the product page.
• U2, a role that can do it: the customer.
• E14, the evidence: where the requirement was found.
• Q1, a question about it that is still open.

Three things come out of holding a specification this way. You see the impact first: before you change a rule, you see every requirement, screen and test that depends on it. There is one source for people and agents: people read the specification in a browser, agents build the product from the same files. And nothing gets lost: every requirement says where it came from, and every open question stays visible until someone answers it.
```

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

`[IMAGE 03 — images/03-document-versus-graph.png]`

Caption:

```
On the left, the same rule appears on four pages and nothing connects them. On the right it is written once, and everything that depends on it points at it.
```

Body:

```
Because the links are stored rather than implied, a computer can follow them. Change rule B1, and the graph knows exactly which requirements, screens and components depend on it. You do not have to search, and you do not have to remember.

A link reads like a short sentence: SC3 shows R4, R4 follows B1. There are about twenty kinds of node — goals, requirements, rules, roles, screens, components, API endpoints, open questions — and the letters of an ID tell you the kind: R is a requirement, B a rule, SC a screen. Nobody draws the graph by hand. It is in the files, and every picture of it is made from them.

Words you will see:

• Node — one small fact: a requirement, a rule, a screen, a question.
• Link — a connection with a meaning, such as shows or follows.
• ID — a short name for a node, such as R4 or SC3. Every node has one.
• Requirement — something the product must do, with its reason and its tests.
• Acceptance criterion — a test in plain words: given this, when that, then this.
• Needs review — a node that depends on something that has changed.
• Flow — the steps a user takes to reach a goal, and the screens on the way.
• Prototype — a page that looks and works like the real screen, made before the real product is built.
• Design system — the colours, fonts and spacing that every screen uses.
```

---

## 6. Three parts: a skill, an application, two interfaces

Heading (apply H2):

```
Three parts: a skill, an application, two interfaces
```

Body:

```
specs-builder is not one program. It is three parts, and each is used by someone different. Once the three are clear, the rest of this follows easily.
```

`[IMAGE 04 — images/04-three-parts.png]`

Caption:

```
You talk to the skill. The skill produces the application. The application has one interface for people and one for the agents that build the product.
```

Body:

```
1. The skill is what you talk to. It runs inside Claude Code, Anthropic's assistant for the terminal and the editor. The skill teaches it how to write a specification: what to ask, what to write, and how to check it. You talk in plain words. It can also read an existing codebase, website or pile of documents and write the specification from them. You never edit the files yourself — the skill makes every change, and checks the whole specification before it saves one.

2. The application is what the skill produces. A specification is one folder in your project. It holds the facts as plain text, one file per node, and a small application that travels with them. It needs only Python, runs on your machine, and opens in your browser. Because it lives inside the folder, anyone who receives the folder can read the specification, with or without the skill.

3. The application has two interfaces. The same facts, offered two ways, one for each kind of reader. Nothing is copied between them, so people and agents can never be looking at different versions.

For people: pages in a browser. The document, the graph, the layers, the matrix and a working prototype. People read and explore but do not edit; a button on every page sends a change request to whoever keeps the specification. The whole thing can also be saved as a single HTML file and sent to anyone.

For builder agents: a guide and commands. An AGENTS.md that coding agents read by themselves, a step-by-step build guide, and commands that give exact answers, as JSON when that is what is wanted. An agent asks what to build first, what each part needs, which tests to write, and what has changed since its last build.

A builder agent is an agent whose job is to write the product's code and tests. It does not need the skill: everything it needs is in the folder. So one person can write the specification and an agent somewhere else can build from it, in any language. The agent never changes the specification. When something is unclear it writes a question into an inbox, and a person answers it.
```

---

## 7. See it working

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

## 8. How it works

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

Body:

```
The specification is saved as plain text files in your project, so you own it. It can sit in Git next to the code it describes, with the same history and the same review.

1. You talk, Claude Code asks. You start with one sentence. Claude Code writes down what the sentence already says, then asks only what it cannot know: who signs in, what a word means, what is out of scope. Every answer becomes a node with an ID, and every open question stays visible until someone answers it.

There are three ways in, and you can switch between them at any time. You write, and the skill completes what you wrote and asks about the rest. The skill asks, and writes from your answers. Or you point it at something that already exists — code, a website, documents — and it writes what it finds, recording where it found each fact.

It also adds the cases you did not mention, such as what happens when the cart is empty, and marks each one added until you confirm it. What it will not do is guess a fact about the world: a price, a number, what users do, what the law says. Those are asked, and they stay open questions until someone answers them.

2. What the graph holds. A specification holds a good deal more than requirements. It has six parts, and every part is linked to the requirements it serves.

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
3. People read it, agents build from it. This is where the two interfaces earn their keep. People open the specification in a browser, read the document, walk the graph, click through the prototype — or share the whole thing as one HTML file that needs nothing installed. Builder agents read the same files through commands: they ask questions, get exact answers, and ask what has changed since their last build.
```

`[IMAGE 10 — images/10-one-source-two-readers.png]`

Caption:

```
One source, two kinds of reader. Nothing is made for the agents that people cannot also see.
```

Body:

```
A builder agent follows a fixed procedure, written in the folder. First it checks that nothing has changed without review. It reads the overview, then asks for a plan: the parts to build, in order. For each part, one command gives everything that part needs. It writes the tests first, from the acceptance criteria, and names each test after the criterion — R4.1 — so every test traces back to the requirement it came from. When the build is done and you agree it, the agent records which version of the specification it built from. Next time it asks what has changed since then, and rebuilds only that.
```

---

## 9. A change, step by step

Heading (apply H2):

```
A change, step by step
```

Body:

```
This is the part that matters, and the reason a specification is worth holding as a graph at all. Everything above is arrangement; this is what the arrangement is for.

Here is the change from the top of this article, followed all the way through: a cart can now hold six of a product, not five. The same ten-second edit, in the same product, with the same six places holding a copy of the rule. What is different is that the copies are now linked to the thing they came from, and a link is something a computer can follow.

It runs in five steps, and only the first and third need a person. Before any of them, the application will show you what you are about to be let in for.
```

`[IMAGE 11 — images/11-impact-before-the-change.png]`

Caption:

```
Before anything changes, the application shows what a change to rule B1 would touch: the six nodes that depend on it, how many depend on each of those, and the count — so you know the size of the change before you start.
```

Body:

```
01. You ask, and the graph answers before anything moves.

You tell Claude Code what you want in plain words: six, not five, for requirement R4. Nothing changes yet. The first thing it does is walk the links outward from R4 and report what hangs off it — the product page that shows the requirement, the product card that shows it too, and the buying flow that runs through it. That list is not inferred from the wording, and it is not somebody's recollection of where things are. It is the links themselves, which is why it is complete. Then it stops and waits for your yes. This is the step that has no equivalent in a document: you are being told the size of the change while you can still decide not to make it.
```

`[IMAGE 12 — images/12-change-1-you-ask.png]`

Caption:

```
In the picture: R4 in the middle, and the three nodes a change to it would reach. Nothing is marked yet — this is the graph answering a question, not carrying out an instruction.
```

Body:

```
02. The change lands, and everything leaning on it is told.

R4 now says six. The three nodes that depend on it are marked needs review, and each carries the old wording beside the new, so a reviewer sees what actually moved instead of being told that something did. The visitor role is not marked, and that is worth a moment: U1 can add a product to the cart whether the limit is five or six, so the meaning of its link to R4 did not change, and marking it would be noise. Then Claude Code raises something you did not ask about. Rule B1 still says five, and R4 is supposed to follow B1 — the specification now contradicts itself, and it says so rather than letting you find out later.
```

`[IMAGE 13 — images/13-change-2-marked.png]`

Caption:

```
In the picture: three boxes turn amber, R4 turns green, and the visitor stays grey. The amber is not a warning about the change; it is a list of what has not been read yet.
```

Body:

```
03. Every marked node is read again, by a person.

You change B1 too, and the contradiction goes. Then the marked nodes have to be reviewed one at a time: the product page, the product card, the buying flow. Confirming one is deliberately not a button you can click through. The application prints a short code next to the new wording and asks for it back — a small mechanism with a large effect, because it means nobody can approve a node without having the new words in front of them. It is the one part of this that is not automated, and it is the part that should not be: a machine can tell you what a change touches, but only a person can say whether the new wording is right.
```

`[IMAGE 14 — images/14-change-3-reviewed.png]`

Caption:

```
In the picture: the amber clears one box at a time as each is confirmed. By the end only the prototype is still outstanding.
```

Body:

```
04. The prototype catches up.

The prototype is built from the screens, so it goes stale the moment a screen does — and it is the thing people actually look at when they want to know what the product does, which makes a stale one worse than no prototype at all. The page is updated where it needs to be: the quantity field offers six now. It is checked and confirmed like everything else. That leaves one thing behind, and it is the big one — the product's own code, written back when R4 said five. Nobody has told the developers. Nobody has to.
```

`[IMAGE 15 — images/15-change-4-prototype.png]`

Caption:

```
In the picture: the prototype turns green. The code is the last box still grey, and it is grey because nothing has rebuilt it yet.
```

Body:

```
05. The code catches up, and the trail is kept.

A builder agent opens by asking the specification one question: what has changed since the version I last built from? It gets back R4, B1 and the nodes that depend on them — not the whole specification, and not a list of files to re-read. It rebuilds that much, writes the tests from the acceptance criteria as they now stand, names each test after the criterion it came from, and records the version it built against so the next question has an answer. What is left behind is the trail: who changed the number, when, why, what it touched, and who read it. In six months, when somebody asks why the limit is six, the answer is in the specification rather than in whoever happens to remember.
```

`[IMAGE 16 — images/16-change-5-code.png]`

Caption:

```
In the picture: everything is green. The same five boxes you started with, in the same places — which is the point of the sequence: nothing moved, the state travelled.
```

Body:

```
How does the graph know what to mark? Not by reading. Each link remembers the version of the node it points at, as of the last time somebody reviewed that link. When the node changes, its version moves on, the two no longer match, and the node at the other end of the link is marked needs review. That is the whole mechanism — a comparison of two numbers, per link.

Being that dumb is the point. Nothing is inferred from the wording, so it cannot miss a dependency because the rule was phrased differently in two places — the failure that made the six places at the top of this article impossible to search. And it cannot over-report either: a node whose link did not change is not marked, so the review list is short enough that people actually work through it. A list that cries wolf gets approved in bulk, and then it is worth nothing.

What a reviewer sees is not a notification saying something changed somewhere. It is the node itself, with the old words struck out and the new ones beside them.
```

`[IMAGE 17 — images/17-what-a-reviewer-sees.png]`

Caption:

```
The quantity field on the product page: two facts it depends on have changed, five struck out and six new, and a code to type back after reading. Its own text still says 1 to 5 — which is exactly what the review is there to catch.
```

Body:

```
The key idea: people change the specification, not the code. The graph shows what each change touches. Agents carry the change into the code. A product owner never has to read code to know what a change means.
```

---

## 10. What each role gets

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

## 11. Compared with what you use today

Heading (apply H2):

```
Compared with what you use today
```

LinkedIn has no tables. The site's comparison grid is written out here as one
line per row, which is how it reads on a phone anyway.

Body:

```
Documents means Word or Confluence, tickets means Jira, design files means Figma.

Each fact is written: many times in documents, many times in tickets, many times in design files — once in a graph.

Links between facts: in the text only, in documents. Some, by hand, in tickets. None in design files. In a graph, every fact, with a meaning.

What a change touches: you search and hope, in documents. Partly, by hand, in tickets. Not shown, in design files. In a graph, shown before the change.

Where a requirement came from: sometimes, in documents and tickets. No, in design files. In a graph, always, with its evidence.

Open questions: lost in comments, everywhere else. In a graph, visible until answered.

Agents can use it exactly: only as text, in documents. Partly, in tickets. No, in design files. In a graph, yes, through commands.

Format: Word or wiki pages, a tracker's database, a design tool's file — or plain text files in Git.

The graph does not replace a task tracker; it replaces the requirements that get copied into one.
```

---

## 12. Questions people ask

Heading (apply H2):

```
Questions people ask
```

Body — each question is a line you can set in bold:

```
Do I need to be a developer to use it? No. You talk to Claude Code in plain words. You install Python and Claude Code once, and the public repository has a getting-started guide written for people who have never opened a terminal.

Where is my data kept? On your computer, as plain text files in your project folder. The application that shows them runs on your computer too, and the files can live in Git like any other source. Claude Code itself sends your conversation to Anthropic to answer you.

What if the AI writes something wrong? Every requirement records where it came from and how sure the specification is about it. Nothing is final until you agree it, and the tool will not let you agree while questions are still open. Every change is logged, with who made it and why.

Which agents can build from it? Any coding agent that can run a command. The folder carries an AGENTS.md that many agents read by themselves, a CLAUDE.md that points Claude Code at it, and a build guide. The agent does not need the skill, and the product can be written in any language.

Can an agent change the specification by itself? A builder agent does not. Its guide tells it to read only, and to write anything unclear into an inbox for the person who keeps the specification. Changes go through the skill, when a person asks, and each one is checked and logged.

Does it replace Jira or Confluence? No. Keep your tracker for planning and tracking the work. What the graph replaces is the requirements that get copied into those tools, so there is one place to link to instead of four to reconcile.

Does it work for a product that already exists? Yes. It can read an existing codebase, website or set of documents and write the specification from them, and each requirement then names the place it was read from. The Voltline example was written that way.

How big can a specification be? Voltline has 541 nodes. The application stays fast well beyond that — it has been tested at 54,000.

What does it cost? specs-builder is free and open source under the MIT licence. Writing a specification needs Claude Code on a paid Claude plan. Reading one needs only Python and a browser.
```

---

## 13. Try it

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
