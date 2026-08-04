# Label vs. Reality

Where's the gap between what a supplement's label claims and what's 
actually worth taking? Which forms, doses, and products are underdosed, 
poorly absorbed, overpriced, or don't even contain what they say?

Real product labels from NIH's Dietary Supplement Label Database (DSLD), 
joined against a hand-built reference table of what actually works.

*Build in progress — the question's fixed, findings will fill in as I go.*

---

## Approach
Loading DSLD product/ingredient data into SQLite, then joining it against 
a reference table I'm building by hand: effective form, effective dose, 
and how solid the evidence is, per ingredient.

## Findings
_Coming as the analysis gets there._

## What I couldn't conclude
_TBD — the honest limits of what this data can support._

## How I'd validate this
_TBD._

## Data
Source: [DSLD](https://dsld.od.nih.gov). Raw files aren't included here 
(large, not mine to redistribute, easy to re-download). See 
`scripts/load_data.md` to rebuild the database yourself.
