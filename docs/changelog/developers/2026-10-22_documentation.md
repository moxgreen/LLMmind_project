# 2026-10-22 — developer changelog

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

Changes made on this day, in order:

- Outdated figures removed or updated in the documentation (documentation)

---

## 18:05 — Outdated figures removed or updated in the documentation

Kind: documentation

Every living document (README, guide, six reference pages; not the changelogs) was checked for
data and conclusions that no longer describe the current workflow or results.

- `docs/reference/clean_run_duration.md`: the job counts predated the region analyses of
  2026-10-14. Replaced with the counts of `snakemake -n --forceall` (35,958 jobs before
  checkpoints): brain-model score and p-value rules 612 → 1,224, relabelling and Spearman 300 →
  600, summary tables 1 → 3, `compute_isc_nearest_neighbours` 4 → 9, new row
  `extract_region_isc_dataframe` (5), brain-model plots 24 → 57, `plot_spearman_alignment`
  12 → 27, similarity-comparison plots 8/8/4 → 19/19/9. Region totals use the measured
  whole-cortex per-job durations. Section 3: ~124 job-hours (was ~115), ~13 h after
  `assemble_nsd_bold` (was ~11 h), total ~33 h (31–36 h; was ~31 h). Spearman rule renamed to
  `compute_spearman_alignment_with_empirical_p_value` in the table.
- `docs/guides/running_and_troubleshooting.md`: duration 31 h → 33 h (section 1); the
  `--forcerun` command under "Leftover outputs from older versions" used the old rule name
  `compute_spearman_alignmentwith_empirical_p_value`, which Snakemake no longer knows.
- `README.md`: duration in the documentation index 31 h → 33 h.
- `docs/reference/fmri_preprocessing.md`, step 6: the `pieman` repeat-averaging figures (median
  ISC 0.133 vs 0.125, r = 0.999) were measured on 2026-10-02 with the nilearn atlas in the wrong
  template; removed.

Checked and still current: the Spearman null means of `statistics.md`, section 6 (recomputed from
`all_spearman_alignment_scores.tsv`: max |null mean| 3.4e-4 Caption Scene, 1.2e-4 NSD, 3.7e-3
Nature Stories, 2.1e-3 Narratives), the region job counts of `brain_regions.md`, section 4, the
NSD repeat-averaging figures (NSD processing unchanged since they were measured), and the model
list. The split-half reliability numbers appear only in the `## Changes` section of
`fmri_preprocessing.md`, as history, and were left there.

### Context

- Request: the developer asked to search the documentation, changelogs excluded, for outdated
  data and conclusions, list them and remove them.
- Files changed: `README.md`, `docs/guides/running_and_troubleshooting.md`,
  `docs/reference/clean_run_duration.md`, `docs/reference/fmri_preprocessing.md`,
  `docs/AI_USAGE.md`.
- Verification: dry run `snakemake --use-conda --cores 4 -n --forceall --quiet rules` on the
  frontend; rule name checked in `workflow/spearman_alignment/Snakefile`; dates of the `pieman`
  figures checked in the developer changelog of 2026-10-02.
