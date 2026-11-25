# 2026-11-25 — changes for users

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

- Reference pages prepared for writing the article (documentation)
- Reference pages corrected after an external audit (documentation)
- Main analysis keeps the last layer; layer-depth pilot results documented (refactor, documentation)

---

## 12:00 — Reference pages prepared for writing the article

Kind: documentation

The pages in `docs/reference/` are now the main source for the article that accompanies the code.
A new page, `docs/reference/study_overview.md`, is the place to start. It gives:

- the study design in a few paragraphs;
- a table of the four datasets (stimuli, subjects, time resolution, number of neighbours);
- a table of all 38 models;
- the main analysis settings and the software versions;
- which page to read for each part of the article;
- which numbers the pipeline can reproduce and which come from one-off checks;
- the limitations of the study;
- a reference list. Entries without a † mark still need checking before submission.

The statistics page now defines the three similarity measures exactly. The embeddings page now
quotes what the cited paper actually says about the best layer depth: about 3/4 of the depth
holds for one model family (OPT), not for all. Nothing in the pipeline or its results changed.

---

## 15:00 — Reference pages corrected after an external audit

Kind: documentation

- The reference list in `docs/reference/study_overview.md` has been checked entry by entry; each
  checked entry has a DOI or arXiv number and a † mark, and the few details that could not be
  checked are named. The missing Gemma 3n, Gemma 4 and Gröger et al. references are now there.
- The overview page now defines the terms used across the pages, for example "Spearman RSA" (the
  comparison of whole similarity structures) as distinct from "Spearman similarity" (one way of
  comparing two stimuli), and says that the "language region" also contains auditory areas.
- It also explains how to tell when a number on the pages was measured, so it can be checked
  before it goes into the article.
- The limitations list is more detailed about the brain regions and the differences between
  models.

---

## 16:30 — Main analysis keeps the last layer; layer-depth pilot results documented

Kind: refactor, documentation

- The main analysis reads every model at its last layer. Another depth is used only when a run
  asks for one, as the layer-depth pilot does.
- The pilot's results are now written down in `docs/reference/model_embeddings.md`: some model
  families align better with the brain at intermediate depths, others at the last layer.
- The option that sets the depth is now written together with the other options of the
  embedding step. Nothing changes in the results, but the next run recomputes every embedding
  and everything after it once.
