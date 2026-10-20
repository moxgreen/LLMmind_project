# 2026-10-20 — developer changelog

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

Changes made on this day, in order:

- Nature Stories TextGrid check writes its tables to files (new_feature, documentation)

---

## 11:55 — Nature Stories TextGrid check writes its tables to files

Kind: new_feature, documentation

Rule `check_nature_stories_textgrids` had no output and printed its tables to stdout, so its
results (reported in the manuscript) existed only as a hand-copied table in
`docs/reference/nature_stories_stimuli.md`.

- `scripts/check_nature_stories_textgrids.py`: new required arguments `--output` and
  `--unexplained_words`. The per-story table (`story`, `r_words`, `same_trs`,
  `net_word_difference`, `unexplained_words`, `r_phones`, `r_semantic`) and the list of TRs with
  unexplained word differences (`story`, `tr`, `difference`, `words`; the `TR ` prefix of the
  printed list is dropped) are written to these files instead of printed. The computation did not
  change.
- `workflow/dataset_processing/nature_stories_dataset/Snakefile`: new constants
  `NATURE_STORIES_TEXTGRID_CHECK` (`results/mind/nature_stories/qc/textgrid_check.tsv`) and
  `NATURE_STORIES_TEXTGRID_CHECK_UNEXPLAINED` (`.../qc/textgrid_check_unexplained_words.tsv`);
  `check_nature_stories_textgrids` declares them as `output:` and passes them to the script;
  `all_nature_stories_dataset` gains the input `textgrid_check`. `all_nature_stories_dataset` is
  not an input of `rule all`, so a normal run does not build the check.
- Documentation: `docs/reference/nature_stories_stimuli.md` (section 4: output files, new command,
  lowest unrounded correlations 0.9957 for words/TR and 0.9985 for phonemes/TR; `## Changes`
  entry); `README.md` (Outputs).

### Context

- Request: the developer asked to save the check results to files, built by the Nature Stories
  dataset target only and not by the whole workflow, so that the numbers quoted in the manuscript
  have a traceable source.
- Files changed: `workflow/dataset_processing/nature_stories_dataset/scripts/check_nature_stories_textgrids.py`,
  `workflow/dataset_processing/nature_stories_dataset/Snakefile`,
  `docs/reference/nature_stories_stimuli.md`, `README.md`, `docs/AI_USAGE.md`.
- Verification: `snakemake -n all_nature_stories_dataset` scheduled only
  `check_nature_stories_textgrids`; `snakemake -n` (rule all) reported nothing to be done. The rule
  was run on the frontend (8 s); the two TSVs equal, after rounding, the table of 2026-10-19 in the
  reference page, and the unexplained-words file lists the same 7 words.
