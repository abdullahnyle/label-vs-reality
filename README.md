# Label vs. Reality

An undergraduate study of supplement label records from NIH's
[Dietary Supplement Label Database](https://dsld.od.nih.gov).

The creatine analysis is being reintroduced in small, reviewed changes after an
oversized commit was removed. The files currently on `main` are exploratory;
they do not yet reproduce the complete case study. Earlier claims about effective
doses and product-name matches should not be used.

The completed snapshot analysis and its evidence are preserved on
[the recovery branch](https://github.com/abdullahnyle/label-vs-reality/tree/recovery/source-audit-76f8225).
That branch is an archive, not the current supported workflow.

The source audit reproduced 70.7% using maximum recorded amounts and 61.0% using
minimum amounts among usable on-market label IDs. Those are label-amount screens,
not findings about effectiveness, actual contents or daily intake.

Code and project documentation are covered by [MIT](LICENSE); third-party label
images are not relicensed by this repository.
