# 2026-11-25 — developer changelog

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

- Reference pages prepared as the main source for the article (documentation)

---

## 12:00 — Reference pages prepared as the main source for the article

Kind: documentation

- New `docs/reference/study_overview.md`, the entry point for writing the article: study design;
  dataset table counted from `results/mind/<dataset>/manifests/` (Narratives 18 stories, 324
  subjects, 14–75 per story, 681 scans; Nature Stories 11 × 11; NSD and Caption Scene 1000 images,
  8 subjects each, every image seen by all 8; Caption Scene repeats 1–2, mean 1.99); the 38 models
  from `config/config.yaml` with HF IDs, `parameters_millions` and quantisation; analysis parameters
  with links to their home pages; package versions pinned in `workflow/**/envs/*.yaml`; a map from
  article parts to pages; which numbers the workflow reproduces (the `results/tsv_summaries/` tables,
  the figures) and which come from one-off checks (statistics section 8, NSD trial history, image
  overlap, regional crossover, corrected Nature Stories onsets); limitations, each linked to its
  home; a reference list, two entries checked against the publication, the rest flagged for
  checking.
- `docs/reference/statistics.md`, section 1: the three similarity types defined as
  `compute_similarity.py` computes them (L2; centring + L2; average ranks + centring + L2, then dot
  product), only model vectors capped, and ties at the *k*-th neighbour broken by `np.argpartition`
  order in `compute_blockwise_topk_from_embeddings()`.
- `docs/reference/model_embeddings.md`, section 3: the "best layer near 75%" claim replaced by what
  Antonello, Vaidya & Huth (2023, arXiv:2305.11863 v4, section 3.1) state: OPT peaks "roughly 3/4
  into the model" (OPT-30B layer 33/48), LLaMA early (LLaMA-33B layer 18/60). Caucheteux & King
  (2022) could not be fetched (nature.com login redirect) and are marked unchecked.
- `docs/reference/fmri_preprocessing.md`, section 1 sources: the Narratives confound note now gives
  the paper's DOI (10.1038/s41597-021-01033-3) and the list as a second automated summary reports it
  (6 motion parameters, 5 PCs of eroded CSF + WM masks, cosine 128 s, single regression model);
  the PMC methods text was not reachable verbatim (truncated page; the PDF returned a reCAPTCHA),
  so the warning stays.
- `README.md`: the documentation index lists the new page first and says that `docs/reference/` is
  the article's main source; the Models section links to the model table.

### Context

- Request: "the documentation of LLMmind_project in 'reference/' should be use as the main source
  to write the article coming with the code. update it accordingly".
- Files changed: `docs/reference/study_overview.md` (new), `docs/reference/statistics.md`,
  `docs/reference/model_embeddings.md`, `docs/reference/fmri_preprocessing.md`, `README.md`,
  `docs/AI_USAGE.md`, this file and its user counterpart.
- Verification: counts recomputed from the manifests with a one-off script; model table and
  parameters compared with `config/config.yaml`; package versions read from the env files;
  similarity and tie handling read from `compute_similarity.py` and `compute_nearest_neighbours.py`;
  citations checked by fetching the arXiv and PMC pages. No code or result changed.
