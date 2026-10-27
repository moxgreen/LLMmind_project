# 2026-10-27 — developer changelog

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

Changes made on this day, in order:

- Near-constant tolerance removed from the ISC; leftover Caption Scene parcel files deleted (removal, documentation)

---

## 11:09 — Near-constant tolerance removed from the ISC; leftover Caption Scene parcel files deleted

Kind: removal, documentation

`workflow/libraries/compute_isc.py`:

- Removed `CONSTANT_SIGNAL_RTOL` (`8*float32 eps`, about 9.5e-7) and `is_constant_signal()`
  (`ptp(x) <= CONSTANT_SIGNAL_RTOL*max|x|`). `compute_leave_one_out_isc()` no longer sets r to 0
  for such signals.
- Replaced `np.nan_to_num(r, nan = 0.0, posinf = 0.0, neginf = 0.0)` with a check: if any r is
  not finite (0/0 from an exactly constant time course), a `ValueError` names the subject index
  and the parcels. No other caller used the removed names.

Check before the change (read-only, on the stored parcel time series, grouped as each
`compute_*_isc.py` script groups them; the recomputed ISC matched every stored file exactly):

| Dataset | Stimuli | Zeroed by the tolerance | Exactly constant | Non-finite r without the check |
|---|---|---|---|---|
| Nature Stories | 11 | 0 | 0 | 0 |
| Narratives | 18 | 0 | 0 | 0 |
| Caption Scene | 1000 | 0 | 0 | 0 |
| NSD | 1000 | 2 | 0 | 0 |

The 2 NSD cases are the leave-one-out mean of the other subjects in a 3-volume window:
`nsd-06445` parcel 39 (held-out subject 6, range 0.0008 around 1023.8, r = −0.53) and
`nsd-43747` parcel 26 (held-out subject 2, range 0.0006 around 1084.3, r = −0.61). Their ISC
changes by 0.0666 and 0.0757; all other ISC values are unchanged (difference ≤ 3e-8, float32
storage).

**Stored results not rebuilt.** The `compute_*_isc` rules are `shell:` rules without a
`code_version()` param, so Snakemake does not rerun them after this edit. The stored
`task-nsd-06445_isc_mean.npy` and `task-nsd-43747_isc_mean.npy`, and everything downstream of the
NSD ISC, still hold the old values until `--forcerun compute_nsd_isc` (or a full recomputation).

Leftover files: `results/mind/caption_scene/parcels/task-*/` held 31,800 `.npy` files for the
15,900 rows of `csd_events_manifest.tsv`. The 15,900 extra files used unpadded numbers
(`sub-1_ses-13_run-50_…`), all dated 2026-09-24, one per current file. They were listed by
comparing the folder with the paths built as in `caption_scene_parcel_path()`, after checking
that every manifest path exists, and deleted from that explicit list. Added to "Leftover outputs
from older versions" in the guide.

### Context

- Request: the developer asked why Pearson r values were mapped to 0 below about 1e-6, chose to
  remove the tolerance to keep data manipulation to a minimum, approved the change after the
  read-only count above, and asked to delete the leftover files found during the count.
- Files changed: `workflow/libraries/compute_isc.py`, `docs/reference/fmri_preprocessing.md`
  (step 6 and `## Changes`), `docs/guides/running_and_troubleshooting.md`, `docs/AI_USAGE.md`.
- Verification: the new code recomputed `nsd-06445`, `nsd-43747` (only parcels 39 and 26
  changed) and `nsd-02951` and Nature Stories `life` (difference 0.0); a synthetic input with a
  constant parcel raised the `ValueError` naming that parcel. After the deletion, 15,900 parcel
  files remain and none has an unpadded name.
