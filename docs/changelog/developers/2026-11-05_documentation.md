# 2026-11-05 — developer changelog

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

Changes made on this day, in order:

- Robustness checks of model size, Narratives dependencies and story duration recorded (documentation)

---

## 18:20 — Robustness checks of model size, Narratives dependencies and story duration recorded

Kind: documentation

`docs/reference/statistics.md`, new section 8, records three one-off checks; no pipeline code or
result changed:

- **Model size.** Spearman between log10(`parameters_millions`) and RSA coefficient or enrichment,
  permuted within `model_family()`, two-sided around the null mean, BH per modality: 0/24 for
  language, vision and language without quantised models. Exact 5! tests for `bloom_*` and `gemma3_*`.
- **Narratives dependencies** (IS20). 72 one-unit-per-block subsets with `compute_similarity`
  normalisation and 10,000 relabellings, plus 240 exact restricted permutations (both pairings of
  the swapped blocks). The restricted null led to an exploratory leave-units-out analysis: without
  both Shapes units the median ρ falls to −0.008 / 0.030 / 0.156 and 0/24 models survive under each
  similarity type.
- **Duration and length.** Partial RSA on rank-transformed pairwise similarities with covariates
  −|Δlog duration| and −|Δlog `n_tokens`|, relabelling the model residual matrix. Narratives stays
  24/24; Nature Stories moves from 0/0/1 to 0/0/2 (duration) and 0/0/1 (tokens).

IS20 and I20 were removed from `.claude/SUGGESTIONS/LLMmind_project.md`, since that check is done.

### Context

- Request: the developer asked to run the model-size, dependency and duration proposals in the
  scratchpad after the supervisor's critique of the manuscript.
- Files changed: `docs/reference/statistics.md`, `docs/AI_USAGE.md`, the two changelogs of this day.
- Verification: the scripts reproduce all published Narratives and Nature Stories coefficients to
  within 10⁻⁵; 240 distinct restricted permutations and 36 fixed pairs were asserted or counted;
  identical p-values across block pairings were traced to swapped permutations never reaching the
  observed ρ. The environment was the Spearman rule's conda environment (numpy 2.5.3, scipy 1.18.1,
  pandas 3.0.6). The scripts are not in the repository.
