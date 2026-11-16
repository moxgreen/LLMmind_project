# 2026-11-16 — changes for users

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

Changes made on this day, in order:

- Clearer instructions for placing the raw data (documentation)
- Shorter README with the source of every dataset (removal, documentation)
- Input files that need an extra step, explained for people downloading the data themselves (documentation)

---

## 15:33 — Clearer instructions for placing the raw data

Kind: documentation

The README no longer describes the lab's own storage and download project. It now says that the
raw data were downloaded with a separate workflow, not included because the datasets are very
large, and that to reproduce the analysis you download the listed files and put them in
`resources/datasets/<dataset>/` at the paths given (a symbolic link per dataset is fine).

---

## 15:42 — Shorter README with the source of every dataset

Kind: removal, documentation

- The README now says where each dataset can be downloaded (DOI or address). Note that the
  English Caption Scene captions are not in the public release; they came from the dataset authors.
- Technical details that were in the README (how stimuli are excluded, where atlases come from,
  configuration checks, the layout of the result tables) now live in the guide and reference pages;
  the README links to them.
- The configuration error messages at startup are explained in the troubleshooting section of the
  guide.
- The old AI-written summary `docs/regional_test_summary.md` was removed; its content is in
  `docs/reference/regional_crossover.md`.

---

## 15:52 — Input files that need an extra step

Kind: documentation

The README section formerly called "Input files not produced by the download" is now "Input files
that are not plain downloads". Three files (the Caption Scene run tables, the Narratives scan
exclusion list and the corrected Nature Stories story onsets) are now made by the download workflow
itself; the section explains what to do if you download the data another way. One file, the
English Caption Scene captions, is not public: it was obtained from the dataset authors.
