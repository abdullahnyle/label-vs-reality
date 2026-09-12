# Label vs. Reality

An undergraduate study of supplement label records from NIH's
[Dietary Supplement Label Database](https://dsld.od.nih.gov).

The Python workflow imports the snapshot, matches declarations and compares
minimum/maximum recorded amounts
per label ID. See [reproduction instructions](scripts/load_data.md) and the
[amount-selection check](docs/creatine-amount-selection.md). The SQL files retain exploratory counts and reference queries. The
[case study](docs/creatine-case-study.md) connects the recorded amounts to the
directions and image reviews; it does not establish effectiveness or product contents.

The source audit reproduced 70.7% using maximum recorded amounts and 61.0% using
minimum amounts among usable on-market label IDs. Those are label-amount screens,
not findings about effectiveness, actual contents or daily intake.

Code and project documentation are covered by [MIT](LICENSE); third-party label
images are not relicensed by this repository.
