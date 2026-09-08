# Creatine pipeline verification, 8 September 2026

## Completed original-data verification

The original database and all 16 source CSV files are now available. The archive
ReadMe dates the download to 10 January 2026. Both databases passed SQLite
integrity checks. All 214,780 overview rows and 2,020,130 facts rows agreed after
the documented storage-type, whitespace and blank-value normalization.
An independent Decimal calculation checked all 2,163 matched label IDs without
discrepancies. Source database fingerprints remained unchanged.

Two complete final analysis runs produced identical exports. The suite passed
24 tests. Compilation and whitespace checks passed. The published source
verification JSON and run manifest retain the counts and fingerprints.

Source review covered all 44 named below-threshold candidates and a reproducible
30-record Suggested Use sample. Fifty-eight API amount checks agreed with the
snapshot. Seven label images were inspected; they exposed a likely quantity
transcription issue and a serving-metadata inconsistency. These were purposeful
checks, not a representative error-rate study. Reviews are attributed to ChatGPT;
Abdullah's independent review remains pending.

## Earlier engineering sessions

The following entries are historical. Their missing-data and publication status
statements applied at the time, before the original files became available.


This records work on the prepared implementation, not a dataset result.
The opening sections describe the earlier session; the follow-up is recorded below.
Main remained at `3c9454f`; the original recovery copy remained at `47a70b3`.
No commit, push, merge or history rewrite was made. Only AGENTS.md and the
publication queue were staged. The implementation and research notes remain
prepared in the working tree.

## Changes checked

| Problem | Change and regression evidence |
|---|---|
| A source `NOCASE` collation admitted unlisted ingredient spellings | Forced binary matching and unmatched-name grouping. A synthetic uppercase 20 g declaration no longer changes a 2.5 g matched record. |
| Matched-only exports hid blend and panel context | Exported all facts for matched IDs, separating matched rows from `other_facts`. Tests retain parent-blend rows, null names and a source field sharing an internal alias. |
| Summary readers could miss unknown declarations on otherwise usable labels | Added `partly_unresolved` to sensitivity output and an explicit report count. This overlaps `usable`; it is not another denominator category. |
| A source `rowid` column could replace SQLite's internal row identifier | Rejected shadowing/reserved facts columns and required an ordinary rowid table. |
| A tiny positive decimal could become usable `0.0` during float conversion | Left numerical underflow unresolved. This is a synthetic edge case, not an observed label value. |
| Writer activity beginning after the initial check could escape detection | Rechecked nonempty WAL/journal files before publishing output. A simulated writer-file marker makes the run discard its output. |
| A database created by another process during loading could be overwritten | Used a final hard link instead of rename. The race regression preserves the competing file and fails the import. |
| Direct loader calls accepted invalid acquisition dates | Validated dates inside the loader, not just at the command line. Unknown dates still remain unset. |

The source exporter now uses one ordered facts query, with an indexed temporary
summary table, instead of a facts query per label. It retains one label's full
context at a time; summary records and matched rows are still held in memory.
The eight targeted failure cases above were reproduced before their fixes.
Additional coverage checks malformed CSV rows, blank/duplicate IDs and pending
review fields. Existing mixed-unit, tie, orphan, missing-value and repeatability
checks still pass.

## Checks actually run

```sh
python -m unittest discover -s tests -v
python -m compileall -q scripts tests
python tests/benchmark_pipeline.py --unindexed
python tests/benchmark_pipeline.py
git diff --check
```

All 19 unit/integration tests passed. Compilation and whitespace checks passed.
The scale fixture was generated locally, with 220,000 labels, ten facts per label
and a creatine match every 100 labels. Each of its 2,200 matched labels has two
creatine amounts, 500 mg and 4 g, plus eight surrounding facts. These are invented
test inputs, not observations about supplements.

| Source indexes | CSV import | Analysis 1 | Analysis 2 |
|---|---:|---:|---:|
| Removed before analysis | 5.176 s | 2.704 s | 2.789 s |
| Retained | 5.037 s | 2.127 s | 2.249 s |

Both checks asserted source counts, 2,200 matched IDs, expected minimum/maximum
amounts, the complete surrounding-facts export, identical hashes for every output
file across repeated runs, and an unchanged source database hash. Each database
was 153,481,216 bytes. Environment: Python 3.12.13, SQLite 3.53.1.

Timings are single-machine observations, not a performance guarantee. The fixture
has short fields and simple panel structure. It does not cover the real snapshot's
field lengths, schema differences, acquisition provenance or ingredient patterns.
The unindexed check preceded the final loader hard-link/date change; the indexed
check included it. Both used the same final analysis implementation.

## Reference checks

The original authors' [2017 ISSN position stand](https://link.springer.com/article/10.1186/s12970-017-0173-z),
in its supplementation-protocol section, supports typical 3–5 g/day maintenance
after saturation, with larger-athlete exceptions. It does not validate this
project's per-serving labels or establish product effectiveness.

The official [DSLD API specification](https://api.ods.od.nih.gov/dsld/v9/)
explicitly lists CC0 1.0. The README now links to that directly and limits its
licensing statement to what was verified, without extending it to third-party
label images or trademarks. Both references were checked on 8 September 2026.
The ODS overview page could not be freshly retrieved in full, so no additional
claim was treated as verified from that page in this session.

## Still blocked or limited

The saved `supplements.db` or original DSLD CSV snapshot was not found in the
checkout or attachment searches. No fresh snapshot was substituted. The historical
70.7%, cohort counts, proposed capsule split and earlier sample remain unverified
by this implementation. No manual source-label review was completed.

Source protection assumes a closed, saved database. Hash and writer-file checks
detect observed changes but do not guarantee isolation from every possible live
writer race. The importer requires hard-link support and fails without replacing
the destination if that operation is unavailable.

Next empirical work requires the original bytes: inspect schema and provenance,
run this version, reconcile count changes, and complete source-panel reviews with
evidence and reviewer details. Publishing prepared code follows the separate
eight-hour commit rule in AGENTS.md and docs/commit-queue.md.

## Follow-up review, 8 September 2026

The checkout, latest available handoff, staged rules and fetched GitHub branches
were inspected before further work. No newer remote commit or original source
snapshot was found. The recovery branch contains the original rebuild, not the
subsequent local improvements.

Two concrete failures were reproduced before correction:

- CSV files with an unterminated quoted final field, or trailing text after its
  closing quote, were accepted by the default reader. Strict reading now rejects
  both, discards the import and leaves no destination database. The command-line
  error handler also catches CSV parsing errors. A positive control preserves
  valid multiline directions, escaped quotes and a comma-containing product name.
- A `Market Status` column with NOCASE collation merged `ON MARKET` and `On Market`
  in run.json's raw-value inventory. Binary grouping and sorting now preserve both
  spellings and their separate counts. Their normalized analysis category remains
  `on_market`; this fix concerns provenance, not a new cohort rule.

An additional integration test checks all 48 sensitivity rows for unique keys and
denominator partitions, and seven hand-counted fixture combinations spanning
alias policies, populations, thresholds and minimum/maximum selection. Empty
usable denominators retain a blank percentage, not zero.

`python -m unittest discover -s tests -v` passed all 23 tests. Compilation and
`git diff --check` passed. Full-run repeatability and source-hash preservation
remain covered by the integration suite. No new scale timing is claimed; the
earlier scale measurements above apply to the earlier implementation.

The publication selected for this run is rules-only: AGENTS.md and the queue.
Pipeline changes and this verification record remain queued separately. The
original database/CSV bytes, snapshot reconciliation and actual label reviews
are still missing. Historical percentages are not verified current findings.

### Publication outcome

Created one local commit, `0577e10b6530917d13bdbf887e81dcaae3e7d35e`,
"Recorded repository working rules", at 06:32:33 UTC on 8 September 2026.
It contains only AGENTS.md and docs/commit-queue.md. The exact staged diff was
inspected, whitespace checked, remote refs fetched and all relevant commit times
checked immediately before creation. The newest preceding commit was 47a70b3
at 20:32:27 UTC on 7 September, more than ten hours earlier.

The subsequent Git push failed because HTTPS authentication was unavailable.
No GitHub CLI, credential helper, GH_TOKEN, GITHUB_TOKEN, GIT_ASKPASS or SSH agent
was available. Connected GitHub tools expose commit creation but cannot upload
this exact existing local commit with its original metadata. No second API commit
was created. A fresh remote-ref check confirmed main still at 3c9454f and recovery
still at 47a70b3. No remote history was changed.

Next publication must first deliver this existing rules commit when Git push
authentication and the eight-hour pacing rule permit it. Do not recreate or amend
it through the API. Pipeline and claim-documentation milestones remain queued;
the fixes and follow-up verification record are local, uncommitted work.

## Resume review, 09:00 UTC on 8 September 2026

Fetched origin and checked GitHub main through the connected GitHub reader. Main
remained at `3c9454f`; recovery remained at `47a70b3`. The latest local commit was
still `0577e10` at 06:32:33 UTC, less than three hours earlier. The eight-hour rule
therefore blocked both commit creation and pushing. No push was attempted, and
the earlier Git push authentication failure has not been shown to be resolved.

Reviewed the parser, importer, analysis runner, SQL, methodology and regression
suite. The 23 synthetic tests passed again, including repeatable exports and
unchanged source hashes. No further implementation change was justified by this
review. No new scale benchmark or empirical validation is claimed.

Staged the prepared pipeline files as queue item 2, with proposed message
"Fixed quantity parsing and rebuilt the creatine pipeline". The research prose,
historical records, this verification record and queue update remain unstaged.
The existing rules commit must still be delivered before publishing that stage.

The original database and CSV snapshot remain unavailable. The next substantive
step is to inspect those bytes, run the analysis, reconcile the historical counts
and review source panels. More synthetic testing cannot substitute for that work.
