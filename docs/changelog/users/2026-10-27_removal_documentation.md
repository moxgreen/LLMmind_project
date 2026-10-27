# 2026-10-27 — changes for users

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

Changes made on this day, in order:

- ISC correlations are no longer set to 0 for nearly flat signals; old Caption Scene files deleted (removal, documentation)

---

## 11:09 — ISC correlations are no longer set to 0 for nearly flat signals; old Caption Scene files deleted

Kind: removal, documentation

- **Every ISC correlation is now computed as is.** Before, a correlation was replaced by 0 when
  one of the two signals hardly changed over time. This rule is gone. If a signal is completely
  flat, the correlation cannot be computed, and the run now stops with an error that names the
  brain regions involved, instead of silently writing 0.
- **What changes in the results.** In the current data no signal is completely flat, and the old
  rule affected only 2 values: two NSD images (`nsd-06445` and `nsd-43747`), one brain region
  each, whose ISC changes by about 0.07. Everything else is identical. The stored NSD results keep
  the old values until the NSD ISC is rebuilt, for example with
  `snakemake --use-conda --forcerun compute_nsd_isc` or at the next full run.
- **Old Caption Scene files deleted.** `results/mind/caption_scene/parcels/` held a second, older
  copy of every file, named without leading zeros (`sub-1_ses-13_run-50_…`). The pipeline did not
  use them; they have been deleted. The guide lists them among the leftovers of older versions.
