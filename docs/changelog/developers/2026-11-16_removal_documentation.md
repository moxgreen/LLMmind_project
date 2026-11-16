# 2026-11-16 — developer changelog

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

Changes made on this day, in order:

- README input-data section rid of lab-specific paths (documentation)
- README trimmed to essentials; dataset sources added; leftover Gemini summary removed (removal, documentation)
- README section on hand-made input files updated to the current download workflow (documentation)

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

---

## 15:42 — README trimmed to essentials; dataset sources added; leftover Gemini summary removed

Kind: removal, documentation

- `README.md`:
  - "Input data": new list of the public release of each dataset. Caption Scene: ScienceDB DOI
    `10.57760/sciencedb.27580` (version folder `V1`), with the note that
    `Translated_Image_Caption_pairs.tsv` is not in the release and was obtained from the authors.
    Narratives: OpenNeuro `ds002345` v1.1.4 DOI, downloaded from the authors' DataLad copy (which
    carries `derivatives/afni-smooth/` and `code/scan_exclude.json`). Nature Stories: G-Node DOI and
    archive name; TextGrids from `ds003020`. NSD: S3 bucket, region and the Data Access Agreement.
  - Moved out, each replaced by a one-line link: how `excluded_stimuli` is used (already in
    `model_embeddings.md`); `code_version.py` (already in the guide, section 2); block-wise
    similarity (now `statistics.md` §1); stimulus counts (now `fmri_preprocessing.md` step 1); atlas
    and template sources (now `fmri_preprocessing.md` steps 3–4); startup config checks (now the
    guide, section 6, which also lists `relative_depth`, missing from the README sentence);
    relabelled-scores file and model-model table columns (now `statistics.md` §3).
- `docs/reference/nature_stories_stimuli.md`: "Downloaded by" column (rules of `public_datasets`)
  removed; the public S3 path of the TextGrids moved into the release column.
- `docs/regional_test_summary.md` deleted: it was superseded by `docs/reference/regional_crossover.md`
  on 2026-11-13 but had not been removed.

### Context

- Request: apply the four follow-ups proposed after the first change of the day; check the official
  releases against the sources used by `public_datasets` and explain mismatches.
- Files: `README.md`, `docs/reference/statistics.md`, `docs/reference/fmri_preprocessing.md`,
  `docs/reference/nature_stories_stimuli.md`, `docs/guides/running_and_troubleshooting.md`,
  `docs/regional_test_summary.md` (deleted), `docs/AI_USAGE.md`.
- Verification of sources: Caption Scene DOI and data-availability statement from the *Sci. Data*
  article (PMC13276023); the SciDB share link `6v6NVb` could not be resolved to a DOI automatically
  (JavaScript page), but the folder layout of the 29,350 download links (`V1/sub-01…08`,
  `V1/derivatives`, `V1/stimuli`) matches the record, and the link list contains
  `Image_caption_pairs.tsv` but not `Translated_Image_Caption_pairs.tsv`. Narratives: DOI read from
  the clone's `dataset_description.json`. Nature Stories: G-Node landing page and the archive's
  `datacite.yml`; the six-author list kept in `nature_stories_stimuli.md` is the dataset README's
  "cite this dataset" line, the DataCite record lists four. NSD: AWS Registry of Open Data entry
  and the NSD website. Not verified: whether OpenNeuro `ds002345` itself also hosts the
  `afni-smooth` derivatives.

---

## 15:52 — README section on hand-made input files updated to the current download workflow

Kind: documentation

`README.md`: "Input files not produced by the download" renamed to "Input files that are not plain
downloads". `public_datasets` now produces the three files it listed (rules
`extract_caption_scene_csd`, `copy_narratives_scan_exclude`, `derive_nature_stories_run_onsets`),
so the section now says that the download workflow obtains them with an extra step, which must be
repeated by hand when the data are fetched another way, and that the onsets are found by searching
around each original boundary for the one that leaves every story segment z-scored. The correction
table and the z-scoring check are kept. `Translated_Image_Caption_pairs.tsv`, the only input not in
any public release, is described at the end of the section (moved there from the list of dataset
sources). The anchor in `docs/reference/nature_stories_stimuli.md` follows the new title.

### Context

- Request: update the section now that the changes to `public_datasets` are implemented.
- Files: `README.md`, `docs/reference/nature_stories_stimuli.md`.
- Verified against `public_datasets/workflow/Snakefile` and
  `workflow/scripts/derive_nature_stories_run_onsets.py`. The new rules have not been run yet
  (no `.csd_extracted` marker; the existing `new_run_onsets.json` predates the derivation rule).
