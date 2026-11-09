# 2026-11-09 — developer changelog

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

Changes made on this day, in order:

- Speaker and source table for the Narratives units (documentation)
- Own row of `AI_USAGE.md` brought up to date (documentation)
- One-off checks recorded: Narratives similarity types, Benjamini-Yekutieli, COCO overlap; tie defect of the model-level p-value documented (documentation)
- Narratives dependency check reordered in `statistics.md` (documentation)

---

## 10:00 — Speaker and source table for the Narratives units

Kind: documentation

`docs/reference/statistics.md`, section "Dependencies between the Narratives units": new table with
unit, story, speaker, source and dependency block for the 18 Narratives units, plus a note on what
links each block. No code or result changed.

### Context

- Request: the user noted that the dependency check named speaker blocks but no table said which
  speaker told which story.
- Files: `docs/reference/statistics.md`, both 2026-11-09 changelogs, `docs/AI_USAGE.md`.
- Verification: speakers and sources read from the "Stimuli" section of Nastase et al. (2021),
  *Scientific Data* 8:250 (PMC8479122); the unit list checked against
  `resources/datasets/narratives_dataset/stimuli/transcripts_renamed/` minus `excluded_stimuli.txt`
  (18 units). `task_meta.json` in the Narratives repository has no speaker fields.

---

## 11:55 — Own row of `AI_USAGE.md` brought up to date

Kind: documentation

`docs/AI_USAGE.md`: the latest-AI-edit date of its own row changed from 2026-10-27 to
2026-11-09; the file had been edited on 2026-11-02, 2026-11-05 and 2026-11-09 without
the row being updated.

### Context

- Request: check whether the documentation is up to date.
- Files: `docs/AI_USAGE.md`, both 2026-11-09 changelogs.
- Verification: every row compared with the file's modification time and, for code
  files, the date in its header; this was the only row older than its file's last AI
  edit (ten environment YAMLs are newer only because of a bulk timestamp change on
  2026-10-02 09:50, not an edit).

---

## 14:30 — One-off checks recorded; tie defect of the model-level p-value documented

Kind: documentation

Three approved one-off checks (SUGGESTIONS I17, I21, I22) were run in the scratchpad on the existing
results; no pipeline code or output changed.

- `docs/reference/statistics.md`, section 8, new subsection "Why the similarity types differ on
  Narratives" (I17): brain neighbours and model-level alignment (k = 5, 24 language models)
  recomputed with `compute_leave_one_out_isc()`, `compute_blockwise_topk_from_embeddings()` and the
  pipeline's permutation stream (`default_rng(37)`, 10,000 `permutation(18)`), for the published ISC,
  20 seeded subsamples to 14 subjects per story, the ISC without the 17 highest-mean-ISC parcels,
  and log(ISC + 0.05). Skew explains the Pearson gap; subject count also affects cosine.
- `docs/reference/statistics.md`, section 5, new paragraph "Check under arbitrary dependence"
  (I21): BY q = BH q × Σ1/i, from `model_level_empirical_p_value` and
  `empirical_upper_tail_p_value` of the six whole-cortex and region summary TSVs, study-wide and
  per (dataset, similarity, k) family.
- `docs/reference/fmri_preprocessing.md`, new subsection "Overlap between the Caption Scene and NSD
  images" (I22): 13 shared COCO IDs between the retained sets; NSD `cocoId` via
  `nsdId` = 73k ID − 1, Caption Scene from the file names.
- `docs/reference/statistics.md`, section 3, "Known defect: the model-level test misses ties":
  `aggregate_alignment_scores.compute_model_level_empirical_p_value()` compares float means
  (`null >= observed`) summed in different orders, so exact ties are dropped and p is too small.
  Found because the I17 recomputation, which counts on integer sums, matched the published null
  means exactly but not the p-values. Recorded as TODO P2 with an approved fix (S2), not yet
  implemented.

### Context

- Request: run the approved scratchpad checks I17, I21 and I22; record the tie defect and its fix.
- Files: `docs/reference/statistics.md`, `docs/reference/fmri_preprocessing.md`, both 2026-11-09
  changelogs, `docs/AI_USAGE.md`.
- Verification: the I17 recomputation reproduces the published ISC exactly (max difference 0),
  the observed model-level scores to 4e-11 and the null means exactly; for `bloom_1b1` (Narratives,
  cosine, k = 5) the stored relabelled file gives 1303 null sums ≥ the observed sum and 915 by the
  pipeline's float comparison. The tie counts for Narratives and Nature Stories were recomputed from
  every stored relabelled file of those datasets. NSD's `shared1000` claim was checked on
  `nsd_stim_info_merged.csv` (72,000 images seen by one subject, 1000 by all eight).

---

## 16:06 — Narratives dependency check reordered

Kind: documentation

`docs/reference/statistics.md`, section 8, "Dependencies between the Narratives units": new opening
paragraph (exchangeability assumption of the relabelling null, finding, exploratory status), a
separate paragraph on the Shapes units (moved from the end of the leave-out discussion), and the
restricted-permutation paragraph moved before the leave-out table, which now has a one-line lead.
Content and numbers unchanged.

### Context

- Request: the user asked why the Shapes units received so much attention and whether the docs
  explain it; on the assessment that the reasoning was hard to follow, asked for the edit.
- Files: `docs/reference/statistics.md`, both 2026-11-09 changelogs.
- Verification: every table row and number of the subsection compared before and after the edit.
