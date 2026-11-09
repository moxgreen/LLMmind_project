# 2026-11-09 — developer changelog

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

Changes made on this day, in order:

- Speaker and source table for the Narratives units (documentation)

---

## 10:00 — Speaker and source table for the Narratives units

Kind: documentation

`docs/reference/statistics.md`, section "Dependencies between the Narratives units": new table with
unit, story, speaker, source and dependency block for the 18 Narratives units, plus a note on what
links each block. No code or result changed.

### Context

- Request: the user noted that the dependency check named speaker blocks but no table said which
  speaker told which story.
- Files: `docs/reference/statistics.md`, both 2026-11-09 changelogs, `docs/AI_USAGE.md`.
- Verification: speakers and sources read from the "Stimuli" section of Nastase et al. (2021),
  *Scientific Data* 8:250 (PMC8479122); the unit list checked against
  `resources/datasets/narratives_dataset/stimuli/transcripts_renamed/` minus `excluded_stimuli.txt`
  (18 units). `task_meta.json` in the Narratives repository has no speaker fields.
