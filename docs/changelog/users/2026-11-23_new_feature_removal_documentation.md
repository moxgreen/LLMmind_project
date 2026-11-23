# 2026-11-23 — changes for users

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

- Layer-depth pilot documentation updated after the latest run (documentation)
- The layer-depth pilot runs with one command (new feature, removal, documentation)

---

## 10:00 — Layer-depth pilot documentation updated after the latest run

Kind: documentation

The layer-depth pilot now runs at five depths (25%, 50%, 67%, 75% and 100% of each model) on
both Narratives and Nature Stories. The running guide describes this setup, including how to copy
the brain results of both datasets into each pilot folder, how many jobs to expect (1352 per
depth) and how long a depth takes (about 1 h 20 min on node5).

The 100% pilot reads exactly the same model vectors as the main pipeline, for every model. Its
results differ from the main results only because model values are now capped. The model
embeddings page gives the size of that effect: small on Narratives, larger on Nature Stories.

The times of the 2026-11-20 changes were corrected (12:10 and 12:15 instead of 16:00 and 16:20).

---

## 16:30 — The layer-depth pilot runs with one command

Kind: new feature, removal, documentation

The whole layer-depth pilot now runs with one command from the project root:

```bash
snakemake -s workflow/layer_depth_pilot/Snakefile --cores 4 --resources gpu=1
```

or by submitting `run_snakemake_workflow.sh` on node5. It sets up the folder of each depth by
itself and runs the depths one after the other. The depths are listed in
`config/layer_depth_pilot.yaml` (`relative_depths`). The pilot folders now link to the main brain
results instead of holding copies of them, which frees about 1.7 GB; the pilot cannot change the
main brain results. The README and the running guide describe how to run and rerun it.
