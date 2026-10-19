# 2026-10-19 — changes for users

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

Changes made on this day, in order:

- New check of the Nature Stories transcripts (new feature, refactor, documentation)
- Cough and other non-speech marks removed from the Nature Stories transcripts (bugfix)

---

## 14:10 — New check of the Nature Stories transcripts

Kind: new feature, refactor, documentation

The Nature Stories transcripts come from a different release than the brain data. A new check
compares them with the word and sound counts that the brain data's own authors published, two
seconds at a time. Run it with:

```bash
snakemake --use-conda --cores 1 check_nature_stories_textgrids
```

It prints a table and changes no file. Result: the transcripts contain the words the subjects heard,
at the times they heard them; only 7 of about 23,000 words differ. The details are in
`docs/reference/nature_stories_stimuli.md`, section 4.

---

## 14:10 — Cough and other non-speech marks removed from the Nature Stories transcripts

Kind: bugfix

The transcripts given to the language models contained 15 non-speech marks: `{cg}` (a cough),
`{ig}` and `{sl}`. They are now removed. To apply this to the results, rerun the pipeline with
`--forcerun convert_nature_stories_textgrids`; this recomputes the Nature Stories embeddings and
every result that depends on them. Two misspelt marks, `{ls)` and `(br}`, are still left in.
