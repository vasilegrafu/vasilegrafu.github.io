# Specifications as a graph — for LinkedIn

The site article, cut and reshaped for LinkedIn, with every picture it needs
already rendered. Nothing here is served by the site: `webapp/dist` is what
gets published, and this folder sits outside it.

Source: `https://vasilegrafu.github.io/articles/specifications-as-a-graph`

```
article/
  article.md    the full article, paste-ready, with [IMAGE nn] markers
  cover.png     1920×1080 header, built from the app screenshots
  images/       17 pictures, numbered in the order they appear
post/
  post.md       the feed post that carries the link, with a shorter variant
  post-the-need-and-the-solution.md
                a second post, the argument on its own: the need, then the
                solution, with a shorter variant
  images/       1200×627 pictures for the posts
```

## The order to do it in

1. **Publish the article** from `article/article.md`. Work top to bottom:
   paste a heading and press H2, paste the body block, insert the picture the
   `[IMAGE nn]` marker names, type its caption underneath.
2. **Post the feed post** from `post/post.md`, with the published article's
   link pasted where the text says `{ARTICLE LINK}`.
3. **Later, or to a different audience**, post
   `post/post-the-need-and-the-solution.md`, which makes the same case as an
   argument rather than a story and stands on its own.

## Why the text looks like this

LinkedIn's editor does not understand Markdown — paste `## Heading` and you
get a literal `##`. So `article.md` keeps every heading outside the paste
blocks and tells you which button to press. Same approach as
`linkedin/profile/profile.md` takes for the profile itself.

The paste-ready text runs to about 24,600 characters across 61 blocks, well
inside LinkedIn's 110,000-character limit.

## Why the pictures look like this

The twelve diagrams exist in the site source only as SVG coloured by the
page's own theme variables, and LinkedIn does not accept SVG. Each one is
rendered to PNG at 2× on white through headless Chrome; standalone, the files
fall back to the light palette, which is the one that suits LinkedIn. The
screenshots were already PNG at 2560×1600 and are copied under the number they
carry in the article.

`build_linkedin.py` in the session scratchpad is what rendered them. It is not
kept here: re-rendering is a one-liner against the SVGs, and a script in the
repo would be one more thing to keep in step with the article.

## What was left out, and why

The site article carries 12 diagrams and 15 screenshots. All 27 would be 27
uploads, one at a time, for someone scrolling a feed. This set keeps:

- **Every diagram but one.** `talked.svg`, the example conversation with the
  skill, is the one dropped — it illustrates a paragraph rather than an
  argument.
- **Six screenshots of fifteen**: the requirement with its links, the whole
  specification, one requirement in full, the prototype, the impact view, and
  what a reviewer sees. The other nine are named in the text, with a line
  pointing at the site for them.

Two things in the article do not survive the port and were rewritten rather
than dropped:

- **The comparison table** — LinkedIn has no tables, so each row is written
  out as a sentence.
- **The contents list** — LinkedIn builds its own outline from the headings,
  and it has no anchors to point at.

The six-tile picture of one rule in six places became a list, for the same
reason.
