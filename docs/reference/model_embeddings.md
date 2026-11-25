# Model embeddings: how each stimulus becomes one vector

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../AI_USAGE.md).*

This page describes how `workflow/llm_nearest_neighbours/scripts/get_embeddings.py` turns each
stimulus into one embedding vector per model. These vectors are the model-side representations
whose nearest neighbours are compared with the brain's. Use it as the source for the methods
section. For how to *configure* the chunk length, see section 3 of
[`running_and_troubleshooting.md`](../guides/running_and_troubleshooting.md).

## 1. Stimuli

- One file per stimulus in the dataset's `stimuli_dir` (`config/config.yaml`), read in sorted
  file-name order. The stimulus name is the file name without its extension.
- Stimuli listed in the dataset's `excluded_stimuli` file are skipped. The ISC side applies the
  same file, so both sides cover exactly the same stimuli (checked when the alignment is computed).
- Text stimuli are `.txt` files, read as UTF-8. Image stimuli are `.bmp`, `.jpeg`, `.jpg`, `.png`,
  `.tif`, `.tiff` or `.webp` files. A directory must contain only one of the two kinds.

## 2. Loading the models

- Every model is loaded with `transformers.AutoModel` (the base model, without any language-model,
  classification or projection head) from the local copy in `resources/models/{model}`.
- Weights are loaded in the dtype stored in the checkpoint (`dtype="auto"`), except for the models
  with a `quantization_method` in the config. These are loaded with `bitsandbytes`, in 8 bit
  (`gemma2_9b`, `gemma3_12b`, `gemma4_12b`, `openllama_13b`) or 4 bit (`gemma2_27b`, `gemma3_27b`,
  `gemma4_31b`), so that they fit on one 24 GB GPU.
- All forward passes run in inference mode. Each vector is stored as `float32`.

## 3. Language models (text stimuli)

1. **Tokenisation.** The whole text is tokenised once, without special tokens.
2. **Chunks.** The tokens are split into chunks of at most `max_chunk_length − 1` tokens
   (`max_chunk_length` = 2048 in the config, the same for every language model), overlapping by
   `chunk_overlap` = 256 tokens (config). Chunking stops at the first chunk that reaches the end of the text, so a text that
   fits in one chunk gets exactly one.
3. **BOS token.** If the tokenizer defines a beginning-of-sequence (BOS) token, it is added in
   front of every chunk, so each chunk has at most `max_chunk_length` tokens. All the configured
   tokenizers (BLOOMZ, Gemma 1–4, OpenLLaMA) define one.
4. **Chunk vector.** The chunk is run through the model, and its vector is the **mean of one
   layer's hidden states over all its tokens, including the BOS token** (`pooling: language: avg`
   in the config). The layer is the last one unless `relative_depth` is set (see "Which layer"
   below).
5. **Stimulus vector.** The mean of the chunk vectors, weighted by the number of text tokens in
   each chunk (the BOS token is not counted). Tokens in an overlap therefore contribute to two
   chunks.

The number of tokens and chunks of each stimulus is stored in the `n_tokens` and `n_chunks`
columns of the embeddings file.

**Which layer.** By default (`relative_depth: null` in `config/config.yaml`) the vector comes from
the model's last hidden state. For BLOOMZ, Gemma and OpenLLaMA this is the output of the last
block after the final layer norm, i.e. the input of the next-token prediction head. When
`relative_depth` is a fraction *f* in (0, 1], the `get_embeddings` rule passes
`--relative_depth f`, the model also returns the hidden state after every block, and the vector
comes from block *k* = *f*·*L* rounded to the nearest integer, halves up (*L* = number of blocks;
block 0 is the token embeddings). When *k* = *L* the vector is the default one (the model's last
hidden state). An intermediate block comes before the model's final norm, so before pooling every
token of it is passed through that norm (`ln_f` for BLOOMZ, `norm` for Gemma), as the model does
after its last block: each token then counts with the same scale in the mean, and a few very large
tokens cannot dominate it. Gemma 3n keeps four parallel streams of its hidden state ("AltUp") until
after its last block; at an intermediate block only stream 0 is kept, the one its attention and
feed-forward blocks update (streams 1–3 are cheaper predicted copies in projected coordinates).
Pooling does not change. The final norm is looked up for BLOOMZ and Gemma only: any other model
read at an intermediate depth stops with an error naming it. The normalisation and the Gemma 3n
stream were checked on small randomly initialised BLOOM, Gemma, Gemma 3 and Gemma 3n models
(*f* = 1 gives the default vector; *f* = 0.5 the mean of the normalised tokens). On the real
checkpoints, *f* = 1 gives exactly the default vectors for all 21 pilot models on Narratives and
Nature Stories, quantised Gemma models included; the intermediate depths of the real models ran
without errors but have no reference to be compared with.

`relative_depth` is set only for the layer-depth pilot: `workflow/additional_tests/layer_depth_pilot/Snakefile`
runs the main workflow once per depth listed in `config/layer_depth_pilot.yaml` (25%, 50%, 67%,
75% and 100%), on the five BLOOMZ models and the 16 enabled Gemma models, on Narratives and Nature
Stories (how to run it: [additional-tests guide](../guides/additional_tests.md), section 1).
The BLOOMZ models have
24 blocks (560m, 1b1, 1b7; *k* = 18) or 30 (3b, 7b1; *k* = 23), read from their local
`config.json`. The depth was fixed before any result was seen, from brain-encoding studies of
decoder language models. Antonello, Vaidya & Huth (2023, arXiv:2305.11863, section 3.1) find that
"the OPT models have maximum performance with layers that are roughly 3/4 into the model" (their
best model reads layer 33 of 48 of OPT-30B, about 69%), while their LLaMA models peak "in
relatively early layers" (layer 18 of 60 for LLaMA-33B); 75% therefore rests on OPT, not on every
family. Caucheteux & King (2022, *Commun. Biol.* 5, 134) find that "the middle layers
systematically outperform the output", with "middle layers" defined as the layers from
*L*/2 to 3*L*/4; their example of a middle layer is "the ninth layer of a 12-layer causal
transformer", i.e. 75%. Both papers therefore place the best layer between half and three
quarters of the depth, and 75% is at the upper end of that range. A single depth fixed
in advance is used, rather than the best of several layers, because the best of more layers is
higher by chance alone and larger models have more layers, which would create a size trend by
construction (Gröger, Wen & Brbić 2026, arXiv:2602.14486, Sec. 4.2).

**Decision: the main analysis reads the last layer.** Every result of the main pipeline uses the
model's last hidden state (`relative_depth: null`); another depth is used only where a run
specifies it, as the pilot does. The pilot results below are therefore a sensitivity analysis, not
the main result.

**Layer-depth pilot results.** Run on 2026-11-20 and again from the pilot's own Snakefile on
2026-11-23 (node5, identical tables), with the per-token normalisation and the cap of section 5;
21 models (5 BLOOMZ, 16 Gemma), depths 25/50/67/75/100%. Exact permutation p-values for the
within-family size trends (at most 5 models per family); no correction across depths, similarity
types or families. Outputs: `results/tests/layer_depth_pilot_<D>/results/tsv_summaries/`.

- **Narratives, Spearman RSA by depth** (mean over models, similarity types, whole cortex and
  language region; 25 / 50 / 67 / 75 / 100%):

  | Family | 25% | 50% | 67% | 75% | 100% |
  |---|---|---|---|---|---|
  | BLOOMZ | 0.497 | 0.526 | 0.527 | 0.517 | 0.494 |
  | Gemma | 0.508 | 0.506 | 0.514 | 0.476 | 0.470 |
  | Gemma 2 | 0.498 | 0.494 | 0.471 | 0.456 | 0.439 |
  | Gemma 3 | 0.492 | 0.492 | 0.475 | 0.465 | 0.526 |
  | Gemma 3n | 0.482 | 0.511 | 0.428 | 0.476 | 0.488 |
  | Gemma 4 | 0.479 | 0.507 | 0.471 | 0.476 | 0.536 |

  BLOOMZ, Gemma and Gemma 2 align best at intermediate depths and worst at the last layer; Gemma 3
  and Gemma 4 align best at the last layer (best depth per case: Gemma 3 21/30, Gemma 4 16/24). No
  single relative depth suits every architecture. Local alignment (5 nearest neighbours) is
  flatter, highest at 25–67% for every family except Gemma 3n.
- **Narratives, significance:** RSA p < 0.05 in every case at every depth; local alignment
  p < 0.05 in 93 / 94 / 90 / 83% of cases at 25–75%, against 75% at the last layer.
- **Narratives, model size:** no significant positive trend within any family at any depth.
  Gemma 3 RSA in the language region decreases with size at 67% and 75% (ρ = −1, p = 0.017, all
  three similarity types). Pooled over the 21 models, RSA decreases with size at 67–75% (9 of 12
  conditions, ρ −0.51 to −0.75; t approximation) and is flat at the last layer; this pooled trend
  is confounded with family, since the largest models are mostly Gemma 3 and 4.
- **Nature Stories** (11 stories, RSA only): weak at every depth (RSA p < 0.05 in 19 / 11 / 14 /
  22 / 32% of cases at 25–100%); too few stories to support a depth choice.
- **Caveat.** Choosing a depth for the main analysis from these numbers would be a maximum over
  layers, the selection the fixed-depth design avoids; this is one reason the last layer is kept.

**Caveat: a few very large dimensions.** In BLOOMZ-560m, on one Narratives story, the three
largest of the 1024 dimensions hold 38% of the squared norm of the last-layer vector and 50% at
75% depth. Such dimensions dominate cosine and Pearson similarity but not Spearman similarity,
which uses ranks; the pilot compares the three similarity types for this reason. Every model
vector is capped before any similarity is computed (section 5), which bounds these dimensions.

**Caveat: the BOS token is included in the mean.** In many decoder models, Gemma and
Llama-style models in particular, the hidden state at the first position (here the BOS token) is
an outlier: it acts as an "attention sink" and can have a much larger norm than the other tokens.
Averaging over all tokens, BOS included, can therefore pull every stimulus vector toward the same
direction. The effect is largest for short texts, where the BOS is one of few tokens, and for the
first chunk of each text. It shrinks as texts get longer. Every stimulus of a model gets the same
treatment, but a shared offset still compresses the similarities between stimuli, and none of
the three similarity types removes it. At intermediate depths the per-token normalisation above
limits the weight of an outsized BOS, as the final norm does at the last layer; the cap of
section 5 clips what remains. Excluding the BOS
position from the mean would change every language-model embedding and every result downstream,
so it has not been done. The manuscript's methods state that the BOS token is included.

## 4. Vision models (image stimuli)

1. The image is converted to RGB and prepared by the model's own image processor
   (`AutoProcessor`: resizing, cropping and normalisation as defined for that checkpoint).
2. The vector is the **first (CLS) token of the last layer's hidden states**, after the model's
   final normalisation layer (`pooling: vision: cls` in the config, passed to
   `get_embeddings.py --pool`):
   - CLIP, CLIP fine-tuned on ImageNet-12k, and the ImageNet-21k ViTs are `timm` checkpoints,
     loaded through the `transformers` timm wrapper with its head removed. The hidden states are
     timm's `forward_features()` output, so the CLIP projection and the classification heads
     are **not** applied.
   - DINOv2 is loaded as `Dinov2Model`. Its CLS token after the final layer norm is the same
     vector as its `pooler_output`.

## 5. From vectors to neighbours

The embeddings file holds one row per stimulus, stored without any cap. `compute_llm_nearest_neighbours.py`
first caps the values, then normalises the vectors for the chosen similarity (L2 for cosine,
centring + L2 for Pearson, ranks + centring + L2 for Spearman), and keeps the largest configured k
nearest neighbours of each stimulus, excluding the stimulus itself.

**Cap.** As in Huh et al. 2024 (`remove_outliers` in their code, quantile 0.95), every value of a
model's vectors is clipped to ±*c*, where *c* is the mean over all stimuli of the file of each
stimulus' 95th percentile of absolute values (`capped_embedding_matrix()` and `CAP_QUANTILE` in
`workflow/libraries/compute_similarity.py`). *c* is computed on the whole embeddings file, so the
observed neighbours, the relabelled neighbours (computed on the brain's concepts only) and the
Spearman RSA all use the same cap. Brain representations are never capped. On the layer-depth
pilot (Narratives) the cap changed the scores by −0.02 to +0.03 on average per model family; in
Gemma 3 4B at 67% depth the largest value is about 45 900 against a cap of about 73. At the final
layer (pilot at 100% depth against the main results, same vectors), the cap raises the
brain-model scores of the 21 pilot models by 0.01 (nearest neighbours) and 0.02 (RSA) on average
on Narratives, and the RSA by 0.06 on average on Nature Stories (up to 0.42 in single cases,
0.08–0.17 on average for BLOOMZ and Gemma 7B), where the share of cases with p < 0.05 rises from
14% to 32%.

## 6. Sources

The content comes from the code (`get_embeddings.py`, `compute_similarity.py`,
`compute_nearest_neighbours.py`, `config/config.yaml`) and from the installed `transformers`
source (`modeling_timm_wrapper.py`, `modeling_dinov2.py`). The ImageNet-12k fine-tuning of the
`clip_i21k_ft_*` models was checked on the Hugging Face model card of
`timm/vit_base_patch16_clip_224.laion2b_ft_in12k` (an 11,821-class subset of ImageNet-22k).
**Not verified:** the size of the BOS outlier in these specific models was not measured. The
large-dimension figures for BLOOMZ-560m come from a single story (`pieman`, run on CPU).
`hidden_states[L]` equal to the last hidden state was checked for BLOOMZ-560m only (identical
vectors with *f* = 1 and without the option). The quotations from Antonello et al. (2023) were
read on 2026-11-25 in arXiv v4 (sections 3.1–3.3), those from Caucheteux & King (2022) the same
day in the Europe PMC full text (PMC8850612). The Gröger et al. reference was identified from its
arXiv abstract; its Sec. 4.2 was not read.

## Changes

Changes to this page, oldest first. The sections above always describe the current code.

### 2026-09-30 — page written

Written to document the BOS-token pooling, after a project review found it.

### 2026-10-06 16:30 — sources moved into the page

The sources and the "not verified" note of the old attribution block became section 6, and the
block was replaced by the note under the title. The `--pool` option (from `README.md`) is now
mentioned in section 4, and the chunk-length link points to the new guide.

### 2026-10-08 09:43 — chunk overlap and pooling set in the config

The chunk overlap (256) and the pooling (`avg` for text, `cls` for images) were hard-coded in
`get_embeddings.py`; they are now the `chunk_overlap` and `pooling` keys of `config/config.yaml`,
passed by the `get_embeddings` rule. The values did not change.

### 2026-11-13 18:00 — layer read at a configurable relative depth

Section 3 now says which layer the vector comes from and describes the `relative_depth` setting
(null: last hidden state, as before; a fraction: the block at that depth), the layer-depth pilot
that sets it to 0.75 for BLOOMZ on Narratives, and why one depth is fixed in advance. Added a
caveat on the few very large dimensions of BLOOMZ vectors.

### 2026-11-19 10:00 — layer-depth pilot extended to Gemma and to four depths

Section 3 now says that the pilot covers the 16 enabled Gemma models as well as BLOOMZ, and the
depths 25%, 50%, 67% and 75% rather than 75% only.

### 2026-11-19 11:10 — Gemma 3n left out of the layer-depth pilot

Section 3 now says that the pilot runs 14 Gemma models, not 16, and why the two Gemma 3n models
are left out: their intermediate hidden states hold four parallel copies, which `get_embeddings`
cannot pool.

### 2026-11-20 12:15 — intermediate depths normalised per token, Gemma 3n back, model values capped

Section 3: an intermediate block is now passed token by token through the model's final norm
before pooling (it was pooled unnormalised, so a few very large tokens could dominate the mean);
block *L* is read from the last hidden state; Gemma 3n is read at intermediate depths through its
stream 0 and is back in the pilot (16 Gemma models). Vision models are no longer said to support
intermediate depths. Section 5: model vectors are capped before every similarity, as in Huh et al.
2024. The BOS and large-dimension caveats mention both.

### 2026-11-23 10:00 — pilot scope and check on the real checkpoints

Section 3: the pilot now covers Nature Stories as well as Narratives and the depths 25–100%, as
the pilot overlay and run script already did. The vectors read at *f* = 1 by the pilot were
compared with the main pipeline's on the real checkpoints and are identical for every model; the
page no longer says the code is untested on them. Section 5 gives the effect of the cap at the final layer on
both datasets.

### 2026-11-23 16:30 — pilot run by its own Snakefile

Section 3 says that the pilot is run by `workflow/layer_depth_pilot/Snakefile`, with the depths
listed in `config/layer_depth_pilot.yaml`.

### 2026-11-25 12:00 — evidence for the 75% depth checked

Section 3 said that brain-encoding studies of GPT-like models find the best layer near 75% of
the depth and that this still had to be checked. Antonello et al. (2023) state it for OPT only;
their LLaMA models peak early. The page now quotes what the paper says.

### 2026-11-25 15:00 — Caucheteux & King checked; Gröger et al. identified

Section 3 now quotes Caucheteux & King (2022), read in the Europe PMC full text: their "middle
layers" are *L*/2 to 3*L*/4, so 75% is the upper end of the range both cited papers support. The
"Gröger et al." citation now gives the paper (arXiv:2602.14486), identified from its abstract.

### 2026-11-25 16:30 — last layer kept; pilot results recorded

The developer decided that the main analysis keeps the last layer, with other depths used only
where a run specifies them. Section 3 states this and now records the results of the layer-depth
pilot (normalised, capped sweep of 2026-11-20, reproduced by the pilot Snakefile on 2026-11-23),
which until now were only in the project's working notes.

### 2026-11-25 17:30 — pilot Snakefile path

Section 3: the pilot's Snakefile moved to `workflow/additional_tests/layer_depth_pilot/`, with the
other tests outside the main pipeline; how to run it is in
[`additional_tests.md`](../guides/additional_tests.md).
