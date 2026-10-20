# 2026-10-20 — changes for users

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

Changes made on this day, in order:

- The Nature Stories transcript check now saves its results (new feature, documentation)

---

## 11:55 — The Nature Stories transcript check now saves its results

Kind: new feature, documentation

The check that compares the Nature Stories transcripts with the brain data's own word counts used
to print its results on screen only. It now saves them in two tables:

- `results/mind/nature_stories/qc/textgrid_check.tsv`: one row per story, with how well the words
  and sounds per two-second step agree;
- `results/mind/nature_stories/qc/textgrid_check_unexplained_words.tsv`: the few words that still
  differ, with the story and time step where they occur.

The check is not part of a normal pipeline run. Build it with:

```bash
snakemake --use-conda --cores 1 all_nature_stories_dataset
```

The results are the same as before. The details are in
`docs/reference/nature_stories_stimuli.md`, section 4.
