# 2026-11-09 — changes for users

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

Changes made on this day, in order:

- Speaker and source table for the Narratives units (documentation)
- AI usage record corrected (documentation)
- Three robustness checks recorded, and a flaw in some p-values described (documentation)
- Narratives dependency check easier to follow (documentation)

---

## 10:00 — Speaker and source table for the Narratives units

Kind: documentation

The statistics page ([`docs/reference/statistics.md`](../../reference/statistics.md), "Dependencies
between the Narratives units") now has a table saying who told each Narratives story, where it
came from, and which group of related stories it belongs to. No results changed.

---

## 11:55 — AI usage record corrected

Kind: documentation

The date of the latest AI edit of `docs/AI_USAGE.md` itself was out of date and is now
correct. Nothing else changed.

---

## 14:30 — Three robustness checks recorded, and a flaw in some p-values described

Kind: documentation

- **Why Narratives results depend on the similarity measure.** A few brain areas, mostly auditory,
  respond strongly to every story and dominate the comparison under Pearson similarity; removing
  them brings Pearson close to Spearman. For cosine similarity, the different number of listeners
  per story also matters. See the statistics page, section 8.
- **A stricter multiple-testing correction.** The page now shows how many results survive a
  correction that makes no assumption about how the tests depend on each other. Strong effects
  survive; weaker, uniform ones (for example Narratives Spearman alignment under cosine similarity)
  do not. See the statistics page, section 5.
- **Shared images between Caption Scene and NSD.** Only 13 of the 1000 images used in each dataset
  are the same picture. See the fMRI preprocessing page.
- **A flaw in the model-level p-values of the nearest-neighbour test.** Ties with the observed
  score are sometimes not counted, so some p-values are too small, mostly for Narratives and Nature
  Stories. The statistics page, section 3, describes it. A fix has been approved but not yet
  applied; no result changed today.

---

## 16:06 — Narratives dependency check easier to follow

Kind: documentation

The statistics page, section 8, "Dependencies between the Narratives units", now starts by saying why
the check was made (several Narratives stories share a speaker or source, which the significance test
does not account for) and what it found (the Narratives result rests on the two Shapes descriptions).
The steps then follow in the order they were done. No result changed.
