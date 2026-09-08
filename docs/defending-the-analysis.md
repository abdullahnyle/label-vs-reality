# Understanding and discussing the analysis

The useful preparation is to reproduce a small example and explain the choices.
These notes describe the method; they are not a claim that every research step has
already been completed.

## Walk through one label

Suppose a label has two rows: 500 mg and 4 g. Read the raw values, convert to 0.5 g
and 4 g, and calculate the minimum and maximum. The primary screen uses 4 g, so the
label reaches 3 g at its largest observed usable amount. The minimum comparison
uses 0.5 g. Neither answers how much someone actually takes each day.

Then add another row with an unknown amount. The observed maximum stays 4 g, but
the unresolved-row count increases. Add a second 4 g row: there is still one label
ID in the summary. These are the differences the regression tests protect.

## Questions worth being able to answer

**Why use SQL and Python together?** SQL makes the joins and grouped quantities
visible. Python handles strict text parsing, CSV loading and repeatable exports.
The standard library is enough; the project does not need a framework.

**What is counted?** Distinct DSLD IDs. Ingredient rows are not independent
products, and distinct IDs are not guaranteed to be distinct physical products.

**Why the maximum?** It describes the largest usable recorded option. It is one
explicit descriptive choice. Comparing it with the minimum shows how much that
choice affects the result. Source review must still establish what the panels mean.

**Why 3 g?** It is motivated by a daily maintenance reference, but the actual screen
is per serving. Reaching it is a quantity classification, not an efficacy judgment.
The 2.5 g comparison explores sensitivity rather than changing the reference.

**Why not treat missing amounts as zero?** Unknown and absent are different.
Silently converting text to zero invents a measurement and changes the denominator.

**Why keep blends?** They match the broad ingredient question. A separate question
about dedicated creatine products would require eligibility rules applied across
the cohort. A word in the name is only a review aid.

**Why export the other ingredients?** A creatine row alone can hide its relationship
to a blend or serving panel. Keeping surrounding facts lets a reviewer inspect
that context without counting those rows as creatine or guessing what they mean.

**What if a label has both usable and unknown amounts?** It stays in the usable
screen, but its unknown declarations are flagged. The observed maximum does not
resolve those declarations. The partly unresolved count overlaps the usable group.

**Why not calculate daily dose automatically?** This version deliberately stops at
per-serving amounts. Instructions can contain ranges, multiple phases and different
serving bases. A limited extraction could be developed later with its own validation.

**What changed from the earlier attempt?** The pipeline became executable across
all statements, conversion moved ahead of selection, unresolved quantities gained
explicit statuses, and source evidence became exportable. The original 70.7% was reproduced after the rebuild. The result
changed in meaning, not in its headline count: it measures recorded amounts, not
effective products.

**What can the results not tell us?** Actual contents, absorption, adherence,
clinical outcomes, manufacturer intentions or national market prevalence.

**What is still unfinished?** Your personal review of the decisions, an exhaustive
image audit, and any broader cohort or daily-intake study. The original database
has now been reconciled, 44 candidate texts reviewed, 58 API records compared and
seven label images checked. That is a defined review scope, not complete validation
of every source label.

## Practical preparation

1. Run the tests and read the small fixture in tests/test_analysis.py.
2. Explain the mixed-unit example without looking at these notes.
3. Follow one published records.csv row back to
   matched_rows.csv and the original source label.
4. Recalculate a summary denominator by hand, including the unusable group.
5. Compare one maximum/minimum sensitivity pair and explain the difference.
6. Keep a short contribution log of what you personally ran, checked and learned.
   Describe assistance honestly if asked; technical ownership comes from being able
   to inspect, explain and correct the work.


## Three examples to prepare

- Recalculate 648 / 916 and explain where the other 362 on-market records went.
  Then compare 559 / 916. The 89-label difference is caused by serving selection.
- Read label 253763: 2800 mg belongs to four capsules together. Four capsules
  daily means 2.8 g, not four times 2.8 g. Contrast it with label 57461, where
  a 2.5 g two-capsule serving is specified at three meals.
- Inspect image 551 beside its source fields. Its 4200 mg amount agrees with the
  image, but the facts serving metadata says one capsule instead of six. Explain
  why this does not change the amount screen but could break daily-intake logic.

You do not need to memorize every script. Be able to trace one row, explain the
join and denominator, and describe exactly what the source checks do and do not
prove. Keep an honest record of which steps you personally ran and reviewed.
