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
block 0 is the token embeddings). The same applies to vision models. Pooling does not change.
With *f* = 1 the vector is identical to the default one. Intermediate blocks come before the final
layer norm, so their hidden states are not normalised.

`relative_depth` is set to 0.75 only by the overlay `config/layer_depth_pilot.yaml`, which runs
the five BLOOMZ models on Narratives (how to run it:
[running guide](../guides/running_and_troubleshooting.md), section 1). The BLOOMZ models have
24 blocks (560m, 1b1, 1b7; *k* = 18) or 30 (3b, 7b1; *k* = 23), read from their local
`config.json`. The depth was fixed before any result was seen, from brain-encoding studies of
GPT-like models (Caucheteux & King 2022; Antonello et al. 2023, OPT) that find the best layer near
75% of the depth; those figures still have to be checked against the papers. A single depth fixed
in advance is used, rather than the best of several layers, because the best of more layers is
higher by chance alone and larger models have more layers, which would create a size trend by
construction (Gröger et al., Sec. 4.2).

**Caveat: a few very large dimensions.** In BLOOMZ-560m, on one Narratives story, the three
largest of the 1024 dimensions hold 38% of the squared norm of the last-layer vector and 50% at
75% depth. Such dimensions dominate cosine and Pearson similarity but not Spearman similarity,
which uses ranks; the pilot compares the three similarity types for this reason.

**Caveat: the BOS token is included in the mean.** In many decoder models, Gemma and
Llama-style models in particular, the hidden state at the first position (here the BOS token) is
an outlier: it acts as an "attention sink" and can have a much larger norm than the other tokens.
Averaging over all tokens, BOS included, can therefore pull every stimulus vector toward the same
direction. The effect is largest for short texts, where the BOS is one of few tokens, and for the
first chunk of each text. It shrinks as texts get longer. Every stimulus of a model gets the same
treatment, but a shared offset still compresses the similarities between stimuli, and none of
the three similarity types removes it. Excluding the BOS
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

The embeddings file holds one row per stimulus. `compute_llm_nearest_neighbours.py` then
normalises the vectors for the chosen similarity (L2 for cosine, centring + L2 for Pearson, ranks
+ centring + L2 for Spearman), and keeps the largest configured k nearest neighbours of each
stimulus, excluding the stimulus itself.

## 6. Sources

The content comes from the code (`get_embeddings.py`, `compute_similarity.py`,
`compute_nearest_neighbours.py`, `config/config.yaml`) and from the installed `transformers`
source (`modeling_timm_wrapper.py`, `modeling_dinov2.py`). The ImageNet-12k fine-tuning of the
`clip_i21k_ft_*` models was checked on the Hugging Face model card of
`timm/vit_base_patch16_clip_224.laion2b_ft_in12k` (an 11,821-class subset of ImageNet-22k).
**Not verified:** the size of the BOS outlier in these specific models was not measured. The
large-dimension figures for BLOOMZ-560m come from a single story (`pieman`, run on CPU).
`hidden_states[L]` equal to the last hidden state was checked for BLOOMZ-560m only (identical
vectors with *f* = 1 and without the option).

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
