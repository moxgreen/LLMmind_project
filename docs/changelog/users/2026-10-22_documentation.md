# 2026-10-22 — changes for users

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

Changes made on this day, in order:

- Outdated numbers in the documentation corrected (documentation)

---

## 18:05 — Outdated numbers in the documentation corrected

Kind: documentation

- **A full run now takes about 33 hours, not 31.** The estimate did not yet include the language-
  and visual-region analyses, which doubled the brain-model jobs. The details are in
  `docs/reference/clean_run_duration.md`.
- **A command in the troubleshooting guide works again.** The command for rebuilding old Spearman
  tables used a rule name that no longer exists; it now uses
  `compute_spearman_alignment_with_empirical_p_value`.
- **One outdated measurement removed.** `docs/reference/fmri_preprocessing.md` quoted how much
  averaging repeated listens of the `pieman` story changed its ISC, measured before the Narratives
  atlas was corrected. The averaging itself is unchanged.

No result changed.
