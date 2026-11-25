# 2026-11-25 — changes for users

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

- Reference pages prepared for writing the article (documentation)

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
