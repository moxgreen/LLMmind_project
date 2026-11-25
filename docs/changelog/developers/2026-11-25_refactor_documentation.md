# 2026-11-25 — developer changelog

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

- Reference pages prepared as the main source for the article (documentation)
- Audit of the reference pages: references verified, terms defined, numbers dated (documentation)
- Pilot job count and run time corrected in the running guide (documentation)
- Depth flag written in the `get_embeddings` command; last layer kept; pilot results documented (refactor, documentation)

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

---

## 15:00 — Audit of the reference pages: references verified, terms defined, numbers dated

Kind: documentation

Addresses points 2, 4, 7 and 8 of an external documentation audit of 2026-11-25 (the code-related
points 1, 5, 6 and 9 were not acted on).

- `docs/reference/study_overview.md`:
  - section 8 rebuilt: 35 entries, 34 checked (all but timm) (Crossref API, arXiv API and abstract pages, Europe PMC,
    G-Node, Hugging Face cards) and marked †, with DOIs or arXiv IDs; what could not be checked is
    stated per entry (PMLR pages of CLIP, TMLR of DINOv2, NeurIPS of QLoRA, ICML of Huh et al., the
    timm Zenodo DOI). Added: Gemma 3n (model-card citation, no report), Gemma 4 technical report
    (arXiv:2607.02770), Gröger, Wen & Brbić 2026 (arXiv:2602.14486, identified from its abstract),
    LAION-5B, the Caucheteux & King author correction. Corrected: Nature Stories release authors
    (4, 2026, not 6), Allen et al. year of issue and DOI, Li et al. 2026 volume 13, article 905;
  - new subsection "Terms used on these pages" (similarity vs alignment, Spearman similarity vs
    Spearman RSA, concept- vs model-level inference, ISC vs activation, language region =
    language + auditory, total vs effective parameters);
  - section 6: rule for dating a hand-reported number (date next to it or in the page's
    `## Changes`; code = `git log -1 --until=<date>`); dataset and model tables tagged with
    commit `da29acf`;
  - section 7: the regional limitation split into four (group-level regions, auditory parcels,
    ventral temporal cortex, no cross-modality comparison); training objectives added to the
    size confound.
- `docs/reference/model_embeddings.md`: Caucheteux & King 2022 read in Europe PMC (PMC8850612):
  "middle layers" = *L*/2 to 3*L*/4, example layer 9 of 12; Gröger citation completed.
- `docs/reference/statistics.md`: section 6 renamed "Spearman RSA (global alignment)" with the
  distinction from the Spearman similarity type; size analysis states total parameters.
- `docs/reference/nature_stories_stimuli.md`: G-Node release authors corrected.
- `docs/reference/regional_crossover.md`: "Spearman alignment" → "Spearman RSA".
- `docs/reference/brain_regions.md`: language region described as language + auditory at first
  mention.

### Context

- Request: an external audit pasted by the developer, then "proceed with the documentation edits".
- Files changed: the six reference pages above, `docs/AI_USAGE.md`, both changelogs of the day.
- Verification: each reference compared field by field with the record fetched (one-off scripts in
  the session scratchpad, removed); internal Markdown links of `README.md` and `docs/` checked with
  a one-off script: 0 broken. No code or result changed.

---

## 15:15 — Pilot job count and run time corrected in the running guide

Kind: documentation

- `docs/guides/running_and_troubleshooting.md`, section 1 "Layer-depth pilot": 1352 → 1348 jobs
  per depth, run time 1 h 20 min → 1 h 10 min to 1 h 25 min per depth (about 6 h 30 min in all);
  `## Changes` entry added. The 1352 of the 2026-11-20 runs included the four Nature Stories ISC
  jobs (`create_isc_dataframe` and the ISC neighbours) rebuilt in the brain-result copies; the
  pilot Snakefile links the brain results and passes `--allowed-rules` with the nine model-side
  rules only, so they no longer run.
- First full run of `workflow/layer_depth_pilot/Snakefile` on node5, 2026-11-23 15:52–22:19
  (`--forcerun run_layer_depth_pilot`): 6/6 outer jobs, 1348/1348 inner jobs per depth, no errors.
  Every inner job ran for "Missing output files": the model-side outputs of the 2026-11-20 run
  were no longer in the depth directories when it started.

### Context

- Request: "the full Snakemake pilot workflow ended. check the outputs", then "proceed with the
  guide fix and the TODO update". The TODO update had already been made in the 16:30 change
  (P7/S7 closed), so the TODO file was not changed again.
- Files changed: `docs/guides/running_and_troubleshooting.md`, both changelogs of the day.
- Verification (one-off scripts in the session scratchpad, removed): outer and per-depth Snakemake
  logs (job stats, rerun reasons, no error lines); no file in `results/` outside `results/tests/`
  modified during the run; brain folders in each depth directory are links; summary tables hold
  all 21 models for both datasets with no missing values; Narratives RSA means by family and depth
  and the shares of p < 0.05 equal the 2026-11-20 values; the 42 `*_embeddings.parquet` files of
  the 100% depth equal the main ones (max abs difference 0).

---

## 16:30 — Depth flag written in the `get_embeddings` command; last layer kept; pilot results documented

Kind: refactor, documentation

- `workflow/llm_nearest_neighbours/Snakefile`: the module-level `RELATIVE_DEPTH_ARG`, concatenated
  after the closing line of the `get_embeddings` shell text, is replaced by
  `params.relative_depth_arg` (`""` when `config["relative_depth"]` is `None`, else
  `--relative_depth <f>`), written as `{params.relative_depth_arg}` before `--excluded_stimuli`;
  the rule comment on the concatenation is removed. `get_embeddings.py` is unchanged. Rendered
  command: identical options for the main pipeline (no flag), `--relative_depth 0.75` with
  `--config relative_depth=0.75`.
- Rerun cost: the `code` trigger (shell text) and, for 21 jobs, the `params` trigger mark all 100
  `get_embeddings` jobs and everything downstream. The developer stopped the forced main run of
  2026-11-25 11:23 (35,774 jobs from `compute_llm_nearest_neighbours` down, 1% done) so the change
  rides on that rerun: the dry run now plans 35,874 jobs (the same plus 100 embeddings), nothing
  upstream of `get_embeddings`.
- Decision recorded (developer, 2026-11-25): the main analysis keeps the last layer; another
  depth only where a run sets `relative_depth`. `docs/reference/model_embeddings.md`, section 3,
  states it and records the layer-depth pilot results (the normalised, capped sweep of 2026-11-20,
  which the pilot Snakefile reproduced on 2026-11-23; Narratives RSA by family and depth,
  significance, size trends, Nature Stories), previously only in the TODO file.
- `docs/reference/study_overview.md`: pilot no longer "in progress"; "Last layer only" limitation
  states the pilot finding; a block duplicated earlier the same day by the reference-replacement
  script (it matched the inline text "`## Changes` entry" in section 6 instead of the heading) is
  removed.
- `docs/guides/running_and_troubleshooting.md`, section 2: the paragraph on the `get_embeddings`
  command text describes the new parameter.
- TODO: P3/S3 (decided), P4/S4 (done) and P7/S7 (the pilot Snakefile, verified by its real run of
  2026-11-23: same Narratives RSA profile as the 2026-11-20 sweep for every family and depth)
  closed; S8 to be implemented after the rerun.

### Context

- Request: "about P3, we should take the last layer unless specified differently, I will stop the
  run right now, so that you can make this change safely", then "proceed with the changes to
  get_embeddings".
- Files changed: `workflow/llm_nearest_neighbours/Snakefile`, `docs/reference/model_embeddings.md`,
  `docs/reference/study_overview.md`, `docs/guides/running_and_troubleshooting.md`,
  `docs/AI_USAGE.md`, both changelogs of the day (renamed from `2026-11-25_documentation.md`).
- Verification: node5 checked for running Snakemake processes and locks before the edit (none);
  `snakemake <embedding> -n -p --forcerun get_embeddings` with and without
  `--config relative_depth=0.75` shows the expected commands; `snakemake --use-conda -n` plans
  35,874 jobs with reasons "Code has changed" (79) and "Code + Params have changed" (21) for
  `get_embeddings`. Not yet run.
