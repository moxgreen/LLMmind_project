# 2026-11-02 — developer changelog

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

Changes made on this day, in order:

- README: the corrected Nature Stories run onsets shift five boundaries, not six (documentation)

---

## 18:40 — README: the corrected Nature Stories run onsets shift five boundaries, not six

Kind: documentation

`README.md`, section on hand-prepared inputs, entry
`nature_stories_dataset/responses/new_run_onsets.json`: "shifts six boundaries" → "shifts five
boundaries". Comparing `train_stories` in `responses/run_onsets.json` and
`responses/new_run_onsets.json`, five onsets change (avatar 345→343, howtodraw 711→710,
odetostepfather 2673→2674, souls 3079→3078, undertheinfluence 3434→3433); each moved onset is one
boundary between two consecutive stories, and the end of the last story (3737) is unchanged. The
seven stories in the README table are the stories on either side of those five boundaries. The
table itself was already correct, and the manuscript already said five.

### Context

- Request: an external audit of the manuscript (2026-11-02) noted that the manuscript says five
  boundaries and the README six; the developer asked to fix the README.
- Files changed: `README.md`.
- Verification: read both JSON files and listed every `train_stories` entry whose onset or length
  differs.
