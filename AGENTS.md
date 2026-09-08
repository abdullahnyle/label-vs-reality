# Repository working rules

Abdullah has final authority. These rules apply to Git commands and GitHub tools.

## Code and evidence

Write clear, direct code with sensible names. Avoid unnecessary abstraction and
boilerplate. Add comments when the reason for a decision would otherwise be unclear.
Use plain language in documentation. No marketing language, emojis or canned prose.

Keep the methods understandable and defensible by Abdullah. Explain assumptions,
non-obvious choices and limitations. Do not invent findings or describe synthetic
tests as validation of the real data. Preserve source values when a label looks
wrong; record a correction separately only when evidence supports it.

## Commits and publication

Abdullah removed the eight-hour and 24-hour restrictions on 8 September 2026.
There is no mandatory waiting interval. Earlier instructions imposing those limits
or requiring approval of individual commits are superseded.

Finish one coherent piece of work, review and test it, commit it, then push it.
Use a simple, natural, past-tense message describing that change. Do not use
conventional-commit prefixes. Do not split a single change into a burst of tiny
commits, or create commits just because several files changed.

Before publication, refresh the remote and inspect the exact changes. Preserve any
new work by others. Verify that the remote branch contains the published commit
before reporting success. Do not leave local commits waiting for the user to ask.
If Git authentication is unavailable, use the connected GitHub write tools when
possible and verify the branch update. If all publication routes fail, report the
failure and preserve the work; never claim that it was pushed.

Routine implementation and publication decisions do not require another approval.
Commit timestamps must reflect when work happened. Do not backdate them.

## History and source data

Rewrite published history only when explicitly requested. Preserve affected work
and inspect for later commits before any such change.

The earlier rebuild at recovery/creatine-rebuild-47a70b3 is a recovery copy.
Do not merge it wholesale or mistake it for the current analysis. Raw databases
and CSV archives remain excluded from Git. Publish compact, traceable evidence
and generated results with explicit review status.
