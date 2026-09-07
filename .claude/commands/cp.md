---
description: Commit the working tree and push to main. Nothing else.
argument-hint: [commit message]
---

Commit everything in the working tree and push to `main`. This command is my
explicit instruction to commit and push. Do only these steps — no build, no
lint, no waiting for the deploy, no checks afterwards.

1. If `git status --short` is empty, say so and stop. If the branch is not
   `main`, stop and ask.
2. Stage every changed and untracked path from `git status --porcelain`
   explicitly with `git add -- <paths>`. Never `git add -A` or `git add .`.
   Never stage `webapp/node_modules`, `webapp/dist`, or anything that looks
   like a secret; if you see one, stop and ask.
3. Commit. Use `$ARGUMENTS` as the message if given; otherwise write a short
   imperative subject line from the diff, with body bullets only if the change
   spans more than one area. End with the standard attribution trailer.
4. `git push origin main`. No force, no other branches or tags.
5. Reply with one line: the commit hash and subject.
