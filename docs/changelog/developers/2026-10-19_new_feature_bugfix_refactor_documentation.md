# 2026-10-19 — developer changelog

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

Changes made on this day, in order:

- Word-level check of the Nature Stories TextGrids (new feature, refactor, documentation)
- `{cg}`, `{ig}` and `{sl}` removed from the Nature Stories transcripts (bugfix)

---

## 14:10 — Word-level check of the Nature Stories TextGrids

Kind: new feature, refactor, documentation

New rule `check_nature_stories_textgrids` (`workflow/dataset_processing/nature_stories_dataset/Snakefile`)
and script `scripts/check_nature_stories_textgrids.py`. The rule has inputs (the 11 TextGrids,
`run_onsets`, and the new config keys `nature_stories: features_matrix` and `english1000`) but no
output, so it is never part of `rule all` and runs every time it is named:
`snakemake --use-conda --cores 1 check_nature_stories_textgrids`. It prints a TSV table to stdout.

The script rebuilds `numWords`, `numPhone` and `semantic` of the G-Node `features_matrix.hdf` from
the TextGrids: onsets binned at `TR = 2.0045` s, `TRIM_TRS = 5`, `TR_GRID_OFFSET = 0.01` s (all three
found by fitting the released values). `integer_counts()` undoes the z-scoring of `numWords`
(global over the training stories; smallest value taken as 0). `unexplained_differences()` cancels
opposite word differences up to `MAX_JITTER_TRS = 3` TRs apart (boundary jitter) and the script
lists the TRs with differences left. Per story it prints r of words/TR, the fraction of equal TRs,
the net and unexplained word differences, r of phonemes/TR and the mean per-feature r of the
semantic features.

Refactor: `convert_nature_stories_textgrids.py` has a new generator `speech_entries(tier)`, which
yields `(start, lowercased label)` for every non-empty interval whose label is not in `BAD_WORDS`.
`textgrid_to_txt()` now uses it; the check script uses it for the word and phone tiers. The
transcripts it writes are unchanged by the refactor.

Result: words and phonemes agree TR by TR within boundary jitter in all 11 stories (r ≥ 0.996
and ≥ 0.998); 7 unexplained words out of about 23,000 (`{ls)`, `(br}`, two `uh`, `ukgh`, the last
3 words of `odetostepfather`); semantic r ≈ 0.93. Documented in
`docs/reference/nature_stories_stimuli.md`, new section 4, which replaces the note that only
durations had been compared.

### Context

- Request: the developer asked how to test that the downloaded ds003020 TextGrids match the
  stimuli the subjects heard word for word, chose the offline comparison with the G-Node features,
  and asked for it on `main`.
- Files changed: `workflow/dataset_processing/nature_stories_dataset/scripts/check_nature_stories_textgrids.py`
  (new), `workflow/dataset_processing/nature_stories_dataset/scripts/convert_nature_stories_textgrids.py`,
  `workflow/dataset_processing/nature_stories_dataset/Snakefile`, `config/config.yaml`,
  `docs/reference/nature_stories_stimuli.md`, `docs/AI_USAGE.md`.
- Verification: the script was run with the Nature Stories rule environment on the downloaded
  files (table in the reference page); `snakemake -n check_nature_stories_textgrids` schedules the
  single job; the converter, run into a scratch directory, writes the current transcripts minus
  the 15 labels of the next change, identical otherwise.

---

## 14:10 — `{cg}`, `{ig}` and `{sl}` removed from the Nature Stories transcripts

Kind: bugfix

`BAD_WORDS` in `convert_nature_stories_textgrids.py` gains `cg`, `ig` and `sl`. Before, 15 such
labels (11 `{cg}`, 2 `{ig}`, 2 `{sl}`) were written to `stimuli/transcripts/*.txt` and embedded by
the language models. The G-Node word counts leave them out (found by the check above).

The converter is not covered by `code_version()`, so the change is applied only by a forced rerun:
`--forcerun convert_nature_stories_textgrids`. This rewrites the 11 transcripts, which touches
`.stimuli_ready` (`verify_nature_stories_stimuli`) and so reruns the Nature Stories embeddings and
everything downstream of them. Until then, the existing Nature Stories results still include the
15 labels.

Not fixed: the malformed labels `{ls)` (`howtodraw`) and `(br}` (`legacy`), which `strip("{}")`
does not normalise.

### Context

- Request: found by the word-level check; the developer approved the fix (TODO S1, deleted
  once implemented).
- Files changed: `workflow/dataset_processing/nature_stories_dataset/scripts/convert_nature_stories_textgrids.py`.
- Verification: the converter run into a scratch directory gives transcripts equal to the current
  ones with the 15 labels removed (`diff`), and no `{cg}`, `{ig}` or `{sl}` left.
