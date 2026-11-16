# Specifications as a graph — for LinkedIn

The site article, cut and reshaped for LinkedIn, with every picture it needs
already rendered. Nothing here is served by the site: `webapp/dist` is what
gets published, and this folder sits outside it.

Source: `https://vasilegrafu.github.io/articles/specifications-as-a-graph`
Published: `https://www.linkedin.com/pulse/specifications-graph-vasile-grafu-5lh9f/`

`article/article.md` is kept the same as the published article. When the
article is edited on LinkedIn, edit this file to match.

```
article/
  article.md    the published article, paste-ready, with [IMAGE nn] markers
  cover.png     1920×1080 header, built from the app screenshots
  images/       10 pictures, numbered in the order they appear
    unused/     8 pictures from an earlier, longer edition, not in the
                published article
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

The paste-ready text runs to about 11,000 characters across 35 blocks, well
inside LinkedIn's 110,000-character limit.

## Why the pictures look like this

The diagrams exist in the site source only as SVG coloured by the page's own
theme variables, and LinkedIn does not accept SVG. Each one is rendered to PNG
on white through headless Chrome; standalone, the files fall back to the light
palette, which is the one that suits LinkedIn. They were redrawn with larger
type first, so their labels survive LinkedIn's 744px column. The screenshots
were already PNG at 2560×1600 and are copied as they are.

## What was left out, and why

The published article is the argument and a look at the tool, not the manual.
It keeps the scenario, the problem, the idea, five screens and how it works,
and points at the site for the rest. Left out:

- **Three parts: a skill, an application, two interfaces** — the section and
  its diagram (`unused/04-three-parts.png`).
- **A change, step by step** — the impact view, the five steps of a change and
  what a reviewer sees (`unused/11` to `unused/17`).
- **Words you will see**, **Compared with what you use today** and
  **Questions people ask**.
- **The rest of the tour's screenshots** — the "nine more views" line names
  them and points at the site.

The six-tile picture of one rule in six places became a bulleted list, and
the contents list is gone: LinkedIn builds its own outline from the headings.
