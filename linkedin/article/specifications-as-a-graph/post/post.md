# LinkedIn feed post — Specifications as a graph

The post that carries the article. Publish the article first, then paste its
link where the text says `{ARTICLE LINK}`.

**Image**: `images/document-versus-graph.png` (1200×627). A post with its own
picture reads bigger in the feed than the small card LinkedIn builds from a
link, so attach the image and put the link in the text.

**The cut**: LinkedIn hides everything after roughly 140 characters behind
"…see more". The marker below shows where that falls, so the hook has to be
over by then.

---

## The post _(LinkedIn limit: 3,000 characters)_

```
A product manager changes one number. Five becomes six. The edit takes ten seconds.

Finding every other place that number is written takes two weeks.
← LinkedIn cuts about here

The rule lived in six places: the requirements document, a wiki page, the design file, the prototype, a ticket, and the code. Six wordings of the same fact, and not one line between them. Nobody did anything wrong — the person who changed it could see one copy, and nothing in the toolchain could say which five were left behind.

Then a coding agent read the requirement that morning, found five, and built five. Correctly, from what it was given, in four minutes. Agents do not make this problem better. They make it faster.

I have written up the alternative I have been building: hold the specification as a graph instead of as prose. Many small facts, each written once, each linked to the facts that depend on it. You write it by talking to Claude Code in plain words. People read it in a browser. Agents build from the same files. And before anyone changes a fact, the graph shows every requirement, screen, prototype and test that change will touch — not inferred from the wording, but from the links themselves, which is why the list is complete.

The article follows one change all the way through, in five steps, with the pictures from a working example. Only two of the five steps need a person: deciding to make the change, and reading the new words. The rest is a comparison of two version numbers per link — which is as dumb as it sounds, and that is the point. It cannot miss a dependency because the rule was phrased differently in two places, and it cannot cry wolf either.

It is free and open source, and the example opens on your own machine in a few minutes.

{ARTICLE LINK}

#ProductSpecification #RequirementsEngineering #AgenticAI
```

_About 1,860 characters including the hashtags, once the link is pasted in._

---

## If you would rather keep the link out of the post

LinkedIn shows a post with an outbound link to fewer people than one without.
To avoid that, cut the `{ARTICLE LINK}` line from the post, publish it, and put
this in the first comment straight away:

```
The full article, with the pictures: {ARTICLE LINK}

And the tool it is about, free and open source: https://github.com/vasilegrafu/project.specs-builder
```

---

## A shorter variant _(if the long one feels heavy for a feed)_

```
A product manager changes one number. Five becomes six. The edit takes ten seconds. Finding every other place that number is written takes two weeks.

The rule lived in six places — document, wiki, design file, prototype, ticket, code — in six wordings, with nothing linking them. And a coding agent, asked for a new screen that morning, read the old number and built it. Correctly. In four minutes.

My new article is about holding a specification as a graph instead: small facts, each written once, each linked to what depends on it. Before you change anything, it shows you everything that change will touch. Free and open source, with a working example you can open in a few minutes.

{ARTICLE LINK}

#ProductSpecification #RequirementsEngineering #AgenticAI
```

_About 820 characters._
