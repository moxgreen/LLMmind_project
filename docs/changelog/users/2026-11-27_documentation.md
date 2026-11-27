# 2026-11-27 — changes for users

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

- The layer-depth results now include the three OpenLLaMA models (documentation)
- Every additional test is now called a test, the layer-depth pilot included (documentation)

---

## 11:45 — Layer-depth results with OpenLLaMA

Kind: documentation

- The layer-depth pilot now reports all 24 language models. OpenLLaMA behaves like BLOOMZ, Gemma
  and Gemma 2: its Narratives RSA is higher at every intermediate depth than at the last layer.
- The pilot's last-layer numbers are simply the main results, with nothing re-corrected.
- The additional-tests guide explains how to add models to the pilot without recomputing the
  others (about 20 minutes instead of 5 h 30 min).

---

## 13:40 — Every additional test is called a test

Kind: documentation

- The layer-depth pilot is now the layer-depth test, and the other additional tests are the
  Narratives dependency test, the duration and length test, the similarity-type test, the image
  overlap test and the regional crossover test. Only the names in the documentation changed; the
  commands, folders and results are the same.
