# CLAUDE.md

Guidance for Claude Code working in this repository.

## 1. Git safety — read this first

**Do not commit. Do not push. Do not create branches, tags, or PRs — until I explicitly tell you to.**

- Make changes in the working tree and leave them uncommitted. I review them myself.
- When work is done, summarise what changed and stop. Do not offer to commit as a next step; wait for me to ask.
- `/publish` is how I ask: it means verify, commit everything in the working tree, push to `main`, and confirm the deploy (see `.claude/commands/publish.md`).
- When I do ask for a commit, commit only what I asked for. Never `git add -A` / `git add .` blindly — stage the specific paths.
- Never rewrite history: no `commit --amend`, `rebase`, `reset --hard`, `push --force`, `checkout --` over my changes, `clean -fd`, or `stash drop`.
- Never touch the remote: no `push`, `fetch --prune` with deletion, no branch deletion, no `gh pr create/merge`.
- Never skip hooks or signing (`--no-verify`, `--no-gpg-sign`).
- `main` is the deploy branch for a GitHub Pages site (`vasilegrafu.github.io`). A push here is a public production release. Treat it accordingly.

## 2. Other things not to do without asking

- **Deleting or overwriting files** I did not ask you to touch — look at the target first, and say what you are about to remove.
- **Anything outward-facing**: publishing, deploying, posting, sending, or uploading content anywhere outside this machine.
- **Dependency changes**: no `npm install <new-package>`, no version bumps, no lockfile regeneration unless I ask. If a task seems to need a new dependency, propose it and wait.
- **Secrets**: never write credentials, tokens, API keys, or my email address into source, config, commit messages, or anything published. Nothing in this repo should ever contain a secret — it is a fully public static site.
- **Generated / vendored paths**: `webapp/node_modules/`, `webapp/dist/` — never edit by hand, never commit.
- Long-running or background processes (dev servers) are fine, but tell me the port and stop them when done.

## 3. What this repo is

Personal site published to GitHub Pages at `vasilegrafu.github.io`. It was migrated from Astro to a React single-page app in September 2026; the migration plan and the architecture notes are in `docs/`.

```
docs/      # project documentation (plans, architecture, how-tos) — not served, never a build output
webapp/    # Vite + React 19 + TypeScript source
```

Deployment: a GitHub Actions workflow builds `webapp/` and publishes
`webapp/dist` to GitHub Pages on every push to `main`. Build output is never
committed.

## 4. Working in `webapp/`

All commands run from `webapp/`:

| Task    | Command           |
| ------- | ----------------- |
| Dev     | `npm run dev`     |
| Build   | `npm run build`   |
| Lint    | `npm run lint`    |
| Preview | `npm run preview` |

- Stack: Vite 8, React 19, TypeScript 6, React Router 8, Tailwind CSS 4, lucide-react, ESLint 10 (flat config in `eslint.config.js`).
- `npm run build` runs `tsc -b` first — a type error fails the build. Run the build before telling me something works.
- Entry points: `index.html` → `src/main.tsx` → `src/router.tsx` (built from the manifest in `src/routes.ts`).
- Layers, naming and the styling rules are in `docs/ARCHITECTURE.md` — read it before adding a page, part, icon or theme.
- Pages are prerendered at build time and hydrated in the browser; `docs/SEO.md` explains that plus sitemap, RSS, canonical URLs and social previews. Every page must render `PageMetaPart`, and render-time state that differs per visitor must be hydration-safe.
- `public/` is copied verbatim and referenced by absolute path.

## 5. How I want you to work

- Match the style of the surrounding code — no reformatting of files you did not otherwise change.
- Prefer small, reviewable diffs. If a change turns out to be larger than expected, tell me before doing it.
- Verify before reporting: run the build or lint rather than asserting a change works.
- If something in my request is ambiguous in a way that changes the result, ask. Otherwise use your judgement and say what you assumed.
