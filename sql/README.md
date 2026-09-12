# Earlier SQL exploration

The creatine files retain the maintenance reference, historical ingredient list,
market-status counts and raw-unit counts. The old amount analysis ranked values
before unit conversion and reused CTEs outside their statement scope; those
queries and their unsupported dose conclusions have been removed.

Use [the Python workflow](../scripts/load_data.md) to reproduce the current
[creatine case study](../docs/creatine-case-study.md). The
[claim ledger](../docs/claim-ledger.md) records the withdrawn interpretations.
The magnesium files remain separate exploratory work and are not validated by
the creatine tests or source review.
