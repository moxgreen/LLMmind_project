# 2026-11-16 — developer changelog

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

Changes made on this day, in order:

- README input-data section rid of lab-specific paths (documentation)

---

## 15:33 — README input-data section rid of lab-specific paths

Kind: documentation

`README.md`, "Input data":

- "Organising the input data on disk": the paragraph on the lab's `public_datasets` project, the
  cold-storage path, the four `ln -s` commands and the note on the Narratives `/dataset` suffix
  were replaced by a short paragraph: the raw data were downloaded with an auxiliary Snakemake
  workflow outside this repository, whose download rules are left out on purpose (the datasets are
  very large and a run should not fill a disk by mistake); to reproduce, download the files listed
  above and place them at the given paths; dataset directories may be symbolic links.
- "Input files not produced by the download": the opening sentence no longer names
  `public_datasets`. The rest of the section is unchanged for now; it will be revised once the
  pending changes to `public_datasets` are made.

### Context

- Request: keep only strictly necessary information in the README; a reader without access to the
  lab server does not know how its directories are organised.
- Files: `README.md`, `docs/AI_USAGE.md`.
- Verified by reading the rendered section and grepping the README for `public_datasets` and
  `cold` (no matches left).
