---
description: Commit the working tree and push to main, which deploys the site to GitHub Pages
argument-hint: [commit message]
---

Publish the current working tree: commit it and push to `main`, which triggers
the GitHub Actions deploy to https://vasilegrafu.github.io. This command is my
explicit instruction to commit and push — the git rules in CLAUDE.md that
say "wait until I ask" are satisfied by running it.

Do these steps in order and stop at the first failure, reporting what failed.

1. **Preconditions.** Confirm the branch is `main` and `git status --short`
   shows changes. If there is nothing to commit, say so and stop. If the
   branch is not `main`, stop and ask.

2. **Verify.** From `webapp/`, run `npm run lint` and then `npm run build`.
   Both must pass. If either fails, show the output and stop — nothing is
   committed.

3. **Stage.** List every changed and untracked path from `git status
   --porcelain` and stage those paths explicitly with `git add -- <paths>`.
   Never use `git add -A` or `git add .`. Never stage `webapp/node_modules`,
   `webapp/dist`, or anything that looks like a secret or credential; if you
   see one, stop and ask.

4. **Commit.** Use `$ARGUMENTS` as the commit message if given. Otherwise
   write one yourself: a short imperative subject line describing what
   changed (from the diff), plus a few body bullets if the change spans
   more than one area. End the message with the standard attribution
   trailer for this session.

5. **Push.** `git push origin main`. No force, no history rewriting, no
   other branches or tags.

6. **Watch the deploy.** Poll the workflow run for the pushed commit:

   ```sh
   curl -s "https://api.github.com/repos/vasilegrafu/vasilegrafu.github.io/actions/runs?per_page=3"
   ```

   Match `head_sha` to the pushed commit. Check about every 20 seconds
   until `status` is `completed`, for at most 5 minutes. If `conclusion`
   is not `success`, report the run URL and stop.

7. **Check the live site.** Run:

   ```sh
   curl -sI https://vasilegrafu.github.io/ | head -1
   curl -sI https://vasilegrafu.github.io/career | head -1
   curl -s https://vasilegrafu.github.io/career | grep -o '<title>[^<]*'
   ```

   Both should return 200 and the title should be the Career page's. If the
   site still serves the previous build, wait 30 seconds and try once more —
   Pages can lag behind the workflow by a moment.

8. **Report.** In a few lines: the commit hash and subject, the workflow
   result, and the live-site check. Nothing else.
