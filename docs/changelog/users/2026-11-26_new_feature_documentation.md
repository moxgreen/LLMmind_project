# 2026-11-26 — changes for users

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../../AI_USAGE.md).*

- Five extra analyses can now be rerun from the repository as additional tests (new feature, documentation)
- The effect of the start-of-text token on the language models was measured: it changes no result (documentation)

---

## 12:00 — Five extra analyses can now be rerun from the repository

Kind: new feature, documentation

- The checks behind several numbers in the documentation used to be one-off scripts that nobody
  could rerun. They are now additional tests in `workflow/additional_tests/`, next to the
  layer-depth pilot:
  - the Narratives dependency checks (does the Narratives RSA survive related stories?);
  - the duration and length controls;
  - the check of why the similarity types differ on Narratives;
  - the overlap between the NSD and Caption Scene images;
  - the collaborator's regional crossover, which gives exactly the collaborator's numbers.
- They never run with the main pipeline. To run them all, one after the other:

  ```bash
  for test in narratives_dependencies duration_length_controls similarity_type_check image_overlap regional_crossover layer_depth_pilot; do
      snakemake -s workflow/additional_tests/$test/Snakefile --use-conda --cores 4 --resources gpu=1 || break
  done
  ```

  All but the pilot take about 13 minutes together; the pilot takes about 6 h 30 min and needs the
  GPU. Each writes its tables to `results/tests/<test>/`. How to run each one is in
  `docs/guides/additional_tests.md`.
- The documented numbers were replaced by the tests' results on the current outputs. Most moved
  slightly, because the model similarities now cap extreme embedding values. The conclusions hold:
  the Narratives RSA still rests on the two Shapes stories, and duration and length still explain
  none of it. One conclusion changed: removing the few highest-ISC parcels now helps cosine as much
  as Pearson, so skew explains most of the gap between the similarity types.

---

## 14:45 — The start-of-text token changes no result

Kind: documentation

- Each language model reads a special start-of-text token (BOS) before every text, and its output
  for that token was included in the text's vector. This was flagged as a possible distortion,
  especially for the short Caption Scene captions.
- A one-off check removed it from the vectors of all 24 language models and recomputed the
  alignment.
  - About 97% of each concept's nearest neighbours stay the same.
  - Alignment scores change by at most 0.011.
  - Every model that was significant after correction stays significant, and none becomes so.
- The pipeline therefore stays as it is. The details are in `docs/reference/model_embeddings.md`,
  section 3.
