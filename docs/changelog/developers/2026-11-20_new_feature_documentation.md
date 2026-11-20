# 2026-11-20 — developer changelog

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

Changes made on this day, in order:

- Intermediate depths normalised per token; Gemma 3n readable at intermediate depths (new_feature, documentation)
- Model embeddings capped before every similarity (new_feature, documentation)

---

## 16:00 — Intermediate depths normalised per token; Gemma 3n readable at intermediate depths

Kind: new_feature, documentation

- `workflow/llm_nearest_neighbours/scripts/get_embeddings.py`:
  - new `final_norm(model)`: returns `model.ln_f` or `model.norm`, or the same on
    `model.language_model` (multimodal Gemma 3/3n/4 wrappers); raises `ValueError` naming the
    model class if none exists.
  - `hidden_state_at_relative_depth(output, relative_depth, model)` (new `model` argument):
    block k = floor(f·L + 0.5) as before; k = L now returns `output.last_hidden_state` (needed for
    Gemma 3n, whose `Gemma3nTextModel.forward` uses `capture_outputs(tie_last_hidden_states=False)`,
    so its `hidden_states[L]` is the unmerged 4-stream state); for k < L a 4-D state (Gemma 3n
    AltUp streams, `(4, B, T, D)`) is reduced to stream 0 (`altup_active_idx`), then passed through
    `final_norm(model)` inside `torch.inference_mode()` (the outputs are inference tensors, and a
    module with trainable weights raises outside it).
  - `extract_embedding_from_output()` takes `model` and passes it on; `embed_long_text()` and
    `embed_image()` pass their model. Behaviour without `--relative_depth` is unchanged.
- `config/layer_depth_pilot.yaml`: `gemma3n_e2b` and `gemma3n_e4b` back in `model_subset`.
- Not detected by Snakemake (script edit, same shell text): existing pilot embeddings are
  recomputed only with `--forcerun get_embeddings`. The main final-layer embeddings are not
  affected.
- Docs: `docs/reference/model_embeddings.md` (section 3, caveats, `## Changes`),
  `docs/guides/running_and_troubleshooting.md` (section 1, `## Changes`).

### Context

- Request: TODO S6 points 1 and 3 ("okay, apply per-token normalisation to the pilot"; Gemma 3n
  "keep stream 0"), after comparing with Huh et al.'s platonic-rep, which does no per-token
  normalisation.
- Files changed: `get_embeddings.py`, `config/layer_depth_pilot.yaml`, the two docs above,
  `docs/AI_USAGE.md`.
- Verified on CPU with the pipeline's environment (`transformers` 5.18.0) on small randomly
  initialised `BloomModel`, `GemmaModel`, `Gemma3Model` (multimodal wrapper) and
  `Gemma3nTextModel`: f = 1 equals the default embedding for all four; f = 0.5 equals the mean of
  the final-norm-normalised block (stream 0 for Gemma 3n); `final_norm` finds `LayerNorm`,
  `GemmaRMSNorm`, `Gemma3RMSNorm`, `Gemma3nRMSNorm`. Not yet run on the real checkpoints (GPU).

---

## 16:20 — Model embeddings capped before every similarity

Kind: new_feature, documentation

- `workflow/libraries/compute_similarity.py`: new constant `CAP_QUANTILE = 0.95` and function
  `capped_embedding_matrix(embedding_df, concepts = None)`: `extract_embedding_matrix()` of the
  whole file, clipped to ±c with c = mean over rows of each row's 0.95 quantile of |x| (Huh et
  al. 2024, platonic-rep `metrics.remove_outliers`), then the rows of `concepts` if given
  (`ValueError` if any is missing).
- Used, model side only, by `compute_llm_nearest_neighbours.py` (whole file),
  `compute_topk_on_concept_subset()` in `workflow/libraries/compute_relabelled_alignment.py`
  (both relabelling scripts) and `compute_spearman_alignment_with_empirical_p_value.py` (model
  matrix; the brain matrix is unchanged). The cap is computed on the whole file in every case, so
  observed and relabelled neighbours share it.
- Every brain-model and model-model result changes once recomputed. Snakemake does not detect
  the edit (no `code_version()` on these rules): existing results stay uncapped until forced
  (`--forcerun` command in the running guide, section 2).
- Docs: `docs/reference/model_embeddings.md` (section 5), the running guide (section 2 and
  "Leftover outputs from older versions").

### Context

- Request: TODO S6 point 2 ("apply the cap to when similarities are computed (write a shared
  function, should you use it in multiple--more than two--scripts)"); four scripts use it.
- Files changed: `compute_similarity.py`, `compute_relabelled_alignment.py`,
  `compute_llm_nearest_neighbours.py`, `compute_spearman_alignment_with_empirical_p_value.py`, the
  two docs, `docs/AI_USAGE.md`.
- Verified before the change on the stored pilot embeddings (19 models × 5 depths, Narratives;
  the test script reproduced the pipeline's RSA exactly and 550/570 5NN scores, 20 within ≤ 0.022
  from tie-breaking): mean family score changes −0.02 to +0.03. After the change, on
  `gemma3_4b` at 67%: `compute_llm_nearest_neighbours.py` and the Spearman script ran to
  completion; `capped_embedding_matrix` equals `np.clip` at the documented cap for the whole file
  and for a subset; `compute_topk_on_concept_subset` runs; a missing concept raises.
