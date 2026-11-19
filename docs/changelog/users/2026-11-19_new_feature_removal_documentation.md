# 2026-11-19 — changes for users

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

Changes made on this day, in order:

- Layer-depth pilot extended to the Gemma models (new feature, documentation)
- Gemma 3n left out of the layer-depth pilot (removal, documentation)

---

## 10:00 — Layer-depth pilot extended to the Gemma models

Kind: new feature, documentation

The layer-depth pilot, which reads each language model at 25%, 50%, 67% and 75% of its depth
instead of at its last layer, now covers all 16 Gemma models used in the project as well as the
five BLOOMZ models. The Gemma 4 26B A4B model is left out, as in the main pipeline, because it
does not fit on the GPU. Running the pilot again computes only the new Gemma results; the BLOOMZ
results already in each pilot folder are kept.

The large Gemma models are loaded in reduced precision, and Gemma 3n has an unusual internal
structure; neither has been tried at intermediate depths yet, so check their first results
before relying on them. The running guide's pilot section now describes the current four-depth
setup and how to start it.

---

## 11:10 — Gemma 3n left out of the layer-depth pilot

Kind: removal, documentation

The first run of the layer-depth pilot with the Gemma models stopped almost at once: the two
Gemma 3n models (E2B and E4B) cannot be read at an intermediate depth, because inside the network
they keep four copies of their internal state and combine them only at the very end. The pilot now
leaves these two models out and runs the other 14 Gemma models with the five BLOOMZ models. Their
normal (last-layer) results in the main pipeline are not affected.
