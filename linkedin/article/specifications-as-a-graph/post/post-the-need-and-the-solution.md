# LinkedIn feed post — the need, and the solution

A second feed post for the same subject, written as an argument rather than a
story: what is wrong with how a specification is held today, and what
specs-builder does instead. `post.md` is the one that carries the article on
the day it goes out; this one stands on its own and can go out later, or to a
different audience.

**Image**: `images/document-versus-graph-wide.png` (1200×627). The same picture
the article opens its idea with — a document on the left, the same facts linked
on the right — redrawn to fill the frame, so the words in it can be read in a
feed. (`document-versus-graph.png` beside it is the older, smaller rendering
that `post.md` names.)

**Title**: a feed post has no title field, so the first line does that job.
It is the line LinkedIn shows biggest and it counts against the cut below, so
the sentence under it is kept short.

**The cut**: LinkedIn hides everything after roughly 140 characters behind
"…see more". The marker below shows where that falls; delete the marker line
before posting.

---

## The post _(LinkedIn limit: 3,000 characters)_

```
How to write a specification in the AI era: as a graph, not a document.

Every side of a product keeps its own copy of the facts.
← LinkedIn cuts about here

THE NEED

A specification is one problem seen from several sides at once: the goals, the requirements, the rules, the decisions taken and the questions still open, the people, the flows they follow, the screens, a prototype, the API, the code and the tests.

All of it already exists somewhere. It is just spread across whichever tool each side happened to use — a requirements document, a wiki page, the design file, the prototype, tickets in the tracker, a decision in a chat thread, the code and its tests — and every one keeps its own copy, in its own wording.

Keeping them in step is hand work, and nobody's job. The requirements document does not know which screen shows which requirement. The prototype does not know which rule it is obeying. The tests know a name and nothing else.

So one rule — a cart holds up to five of a product — ends up in six of those places, in six wordings, with not one line between them.

Change it, and nothing can tell you which five copies are now wrong. The cost is not the edit, it is the search — and the places nobody found. Two weeks later the product page still stops at five, a test still expects five, and a coding agent asked for a new screen that morning has read the old number and built it. Correctly, in four minutes.

Agents do not make this better. They make it faster.

THE SOLUTION

Hold the specification as a graph instead of as prose: many small facts, each written once, each linked to the facts that depend on it.

You write it by talking. specs-builder is a skill for Claude Code: you say what the product must do in plain words, and it asks only what it cannot know, records where each fact came from, and leaves open questions visible until someone answers them. It will not invent a fact about the world.

It produces an application that travels with the files. People read it in a browser: the document, the graph, a working prototype of every screen. Builder agents read the same folder and ask it questions, and get exact answers back. Nothing is copied between them, so they cannot drift apart.

Before anyone changes a fact, the graph shows everything that change will touch. Not guessed from the wording: each link remembers the version it was last reviewed against, so when a fact changes, everything that leans on it is marked needs review. Being that dumb is the point — it cannot miss a dependency because the rule was phrased differently in two places, and it cannot cry wolf either.

And it is plain text files in your project, in Git beside the code. You own it.

Free and open source. The worked example — 541 nodes, 1,898 links — opens on your own machine in a few minutes.

The write-up, with the pictures: {ARTICLE LINK}

#ProductSpecification #RequirementsEngineering #AgenticAI
```

_About 2,950 characters including the hashtags, once the link is pasted in — close to the 3,000 limit, so trim before you add anything._

---

## If you would rather keep the link out of the post

LinkedIn shows a post with an outbound link to fewer people than one without.
Cut the `{ARTICLE LINK}` line, publish, and put this in the first comment
straight away:

```
The write-up, with the pictures: {ARTICLE LINK}

The tool, free and open source: https://github.com/vasilegrafu/project.specs-builder
```

---

## A shorter variant _(same argument, for a feed that scrolls fast)_

```
How to write a specification in the AI era: as a graph, not a document.

Every side of a product keeps its own copy of the facts.

THE NEED. The facts a specification is made of — goals, requirements, rules, decisions, flows, screens, tests — already exist. They are just scattered across whichever tool each side uses: a requirements document, a wiki page, the design file, the prototype, tickets, the code. Every one keeps its own copy, and keeping them in step is nobody's job. So one rule — a cart holds up to five of a product — lives in six of those places, in six wordings, with nothing linking them. Change it, and nothing can tell you which five are now wrong. An agent asked for a new screen that morning reads the old number and builds it, correctly, in four minutes. Agents do not make this better. They make it faster.

THE SOLUTION. Hold the specification as a graph: many small facts, each written once, each linked to what depends on it. You write it by talking to Claude Code. People read it in a browser, builder agents ask it questions, and before anyone changes a fact the graph shows everything that change will touch — from the links themselves, which is why the list is complete.

Plain text files in your project, in Git beside the code. Free and open source, with an example you can open in a few minutes.

{ARTICLE LINK}

#ProductSpecification #RequirementsEngineering #AgenticAI
```

_About 1,460 characters._
