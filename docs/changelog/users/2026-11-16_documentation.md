# 2026-11-16 — changes for users

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

Changes made on this day, in order:

- Clearer instructions for placing the raw data (documentation)

---

## 15:33 — Clearer instructions for placing the raw data

Kind: documentation

The README no longer describes the lab's own storage and download project. It now says that the
raw data were downloaded with a separate workflow, not included because the datasets are very
large, and that to reproduce the analysis you download the listed files and put them in
`resources/datasets/<dataset>/` at the paths given (a symbolic link per dataset is fine).
