# 2026-11-09 — developer changelog

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

Changes made on this day, in order:

- Speaker and source table for the Narratives units (documentation)
- Own row of `AI_USAGE.md` brought up to date (documentation)

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

---

## 11:55 — Own row of `AI_USAGE.md` brought up to date

Kind: documentation

`docs/AI_USAGE.md`: the latest-AI-edit date of its own row changed from 2026-10-27 to
2026-11-09; the file had been edited on 2026-11-02, 2026-11-05 and 2026-11-09 without
the row being updated.

### Context

- Request: check whether the documentation is up to date.
- Files: `docs/AI_USAGE.md`, both 2026-11-09 changelogs.
- Verification: every row compared with the file's modification time and, for code
  files, the date in its header; this was the only row older than its file's last AI
  edit (ten environment YAMLs are newer only because of a bulk timestamp change on
  2026-10-02 09:50, not an edit).
