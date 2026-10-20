# Nature Stories stimuli: where the transcripts come from and how they match the fMRI data

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../AI_USAGE.md).*

The Nature Stories inputs come from two separate public releases: the fMRI data from one, the
word-level transcripts from another. This page records where each comes from, how the workflow
uses the transcripts, and the check that both releases describe the same stimuli.

## 1. Sources

| Files | Release | Downloaded by |
|---|---|---|
| `responses/S*_BOLD.hdf`, `responses/run_onsets.json`, `mappers/`, `stimuli/*.wav` | "Nature Story Listening 3T fMRI Data", Huth, de Heer, Deniz, Gong, Gallant, Theunissen (Gallant and Theunissen labs), 11 subjects; G-Node GIN, DOI `10.12751/g-node.t4wew2` | `public_datasets`, rule `download_nature_stories_dataset` |
| `stimuli/textgrids/<story>.TextGrid` | "An fMRI dataset during a passive natural language listening task", LeBel, Wagner, Jain, … Huth, *Sci. Data* 10, 555 (2023); OpenNeuro `ds003020`, DOI `10.18112/openneuro.ds003020.v4.0.0`, folder `derivatives/TextGrids` | `public_datasets`, rule `download_nature_story_stimuli` (`aws s3 cp --no-sign-request` from `s3://openneuro.org/ds003020/derivatives/TextGrids`) |

`ds003020` is a different, later Huth lab dataset (Moth Radio Hour stories, its own subjects). Its
84 stories include all 11 Nature Stories stories. The G-Node archive contains the audio of each
story but no transcript or word alignment, which is why the TextGrids are taken from `ds003020`.

The TextGrids hold a `phone` and a `word` tier. Some are in Praat's long text format and some in
its "chronological" format; `convert_nature_stories_textgrids.py` reads both.

## 2. How the workflow uses them

Rule `convert_nature_stories_textgrids` (script `convert_nature_stories_textgrids.py`) keeps only
the **word sequence** of each story: it takes the `word` tier, drops empty intervals and
non-speech labels (`sp`, `{ns}`, `{br}`, `{cg}`, `{ig}`, `{lg}`, `{ls}`, `{sl}`, `sentence_start`,
`sentence_end`; list `BAD_WORDS`), lowercases the words and writes them, space-separated, to `stimuli/transcripts/<story>.txt`. These transcripts
are the text given to the language models. Two malformed labels, `{ls)` in `howtodraw` and `(br}`
in `legacy`, mix two kinds of bracket and are not recognised, so they stay in the transcripts.

The word timings are discarded, and no rule reads the G-Node `.wav` files. The brain side uses
whole stories (see [`fmri_preprocessing.md`](fmri_preprocessing.md)), so nothing aligns individual
words to TRs.

## 3. Check that both releases describe the same stimuli

Done on 2026-10-09 on the downloaded files, with the workflow's own TextGrid parser.

- **TR counts.** `ds003020/derivatives/respdict.json` gives the number of TRs recorded for each
  story. The G-Node data trim 10 TRs at each end of each story before z-scoring, so a G-Node story
  length plus 20 should equal the `ds003020` count.
- **Durations.** The end time (`xmax`) of each TextGrid was compared with the duration of the
  matching G-Node `.wav` file (mapping in `run_onsets.json`, `stimuli_mapping`).

| Story | G-Node TRs + 20 | `ds003020` TRs | G-Node `.wav` (s) | TextGrid end (s) |
|---|---|---|---|---|
| alternateithicatom | 363 | 363 | 706.7 | 706.7 |
| avatar | 387 | 387 | 754.3 | 754.2 |
| howtodraw | 374 | 374 | 728.3 | 728.3 |
| legacy | 420 | 420 | 820.0 | 820.0 |
| life | 450 | 450 | **808.8** | **880.3** |
| myfirstdaywiththeyankees | 378 | 378 | 736.9 | 736.9 |
| naked | 442 | 442 | 865.0 | 865.0 |
| odetostepfather | 424 | 424 | 828.1 | 828.1 |
| souls | 375 | 375 | 730.0 | 730.0 |
| undertheinfluence | 324 | 324 | 627.7 | 627.7 |
| wheretheressmoke (test) | 311 | 311 | 601.9 | 601.9 |

G-Node lengths are those of the corrected `new_run_onsets.json` (see the
[README](../../README.md#input-files-not-produced-by-the-download)).

Findings:

- **Same stimulus versions.** All 11 TR counts agree exactly, and for 10 stories the TextGrid ends
  within 0.01 s of the G-Node audio. Both releases scanned the same recordings of the stories.
- **The corrected run onsets are confirmed independently.** The lengths in `new_run_onsets.json`
  match `ds003020`; those of the archive's original `run_onsets.json` do not (alternateithicatom
  365, avatar 386, howtodraw 373 after adding 20).
- **The G-Node audio of `life` is about 71 s short.** The scan of `life` lasts 450 TRs × 2 s =
  900 s. Like every other story, its TextGrid ends about 20 s before the end of the scan, while
  `train_04.wav` stops at 808.8 s. The TextGrid, and so the transcript, matches what was scanned;
  the G-Node `.wav` file is truncated or a different cut.
- **No effect on the results.** The workflow reads neither the timings nor the `.wav` files.

## 4. Word-level check against the G-Node features

The G-Node release includes per-TR features that its authors computed from their own transcripts
of the stories (`features/features_matrix.hdf`): `numWords` (words per TR), `numPhone` (phonemes per
TR) and `semantic` (the english1000 word vectors of `features/english1000.hdf`, summed per TR).
Rule `check_nature_stories_textgrids` (script `check_nature_stories_textgrids.py`) rebuilds these
three features from the TextGrids and compares them with the released ones. It writes two tables
to `results/mind/nature_stories/qc/`: `textgrid_check.tsv`, one row per story (the columns of the
table below), and `textgrid_check_unexplained_words.tsv`, one row per TR whose words still differ
(story, TR, TextGrid minus G-Node count, the TextGrid words of that TR). The rule is an input of
`all_nature_stories_dataset` only, not of `rule all`, so a normal run does not build it:

```bash
snakemake --use-conda --cores 1 all_nature_stories_dataset
```

How the features are rebuilt (found by matching the released values, not documented by the
release):

- words and phonemes are those kept by the transcript conversion (section 2), counted in the TR
  that contains their onset;
- the TR is 2.0045 s, and the first released TR starts 5 TRs after TextGrid time 0;
- the TR grid is shifted by 0.01 s against the TextGrid times; the best shift varies by about
  10 ms between stories, so some words on TR boundaries fall into the neighbouring TR;
- the released features are z-scored over all 10 training stories together, so `numWords` is
  turned back into integer counts (its smallest value taken as 0) before comparing.

A word counted one to three TRs away from the released count is boundary jitter, not a different
word. The script cancels such pairs and lists every difference left ("unexplained words").

Result on 2026-10-19, rounded from `textgrid_check.tsv` (`r`: Pearson correlation; semantic: mean
over the 985 features). The lowest unrounded values are 0.9957 for words/TR and 0.9985 for
phonemes/TR, both in `wheretheressmoke`:

| Story | r words/TR | TRs with equal count | Net word difference | Unexplained words | r phonemes/TR | r semantic |
|---|---|---|---|---|---|---|
| alternateithicatom | 0.996 | 0.948 | 0 | 0 | 0.999 | 0.934 |
| avatar | 0.997 | 0.962 | 0 | 0 | 0.999 | 0.931 |
| howtodraw | 0.997 | 0.963 | 1 | 1 | 0.999 | 0.924 |
| legacy | 0.998 | 0.973 | 1 | 1 | 1.000 | 0.925 |
| life | 0.997 | 0.967 | 0 | 0 | 1.000 | 0.925 |
| myfirstdaywiththeyankees | 0.999 | 0.989 | 0 | 0 | 0.999 | 0.931 |
| naked | 0.997 | 0.950 | 1 | 1 | 0.999 | 0.930 |
| odetostepfather | 0.997 | 0.965 | 3 | 3 | 1.000 | 0.928 |
| souls | 0.998 | 0.972 | 0 | 0 | 0.999 | 0.920 |
| undertheinfluence | 0.998 | 0.974 | 0 | 0 | 0.999 | 0.932 |
| wheretheressmoke (test) | 0.996 | 0.935 | 1 | 1 | 0.999 | 0.931 |

The 7 unexplained words, out of about 23,000:

- the malformed labels `{ls)` (`howtodraw`) and `(br}` (`legacy`), see section 2;
- one `uh` each in `naked` and `odetostepfather`, and `ukgh` in `wheretheressmoke`, which the
  G-Node transcripts do not count (other `uh` are counted in both);
- the last words of `odetostepfather` ("my life thank you"), counted in its final TR by the
  TextGrid only.

Findings:

- **The TextGrids hold the words the subjects heard, at the times they heard them.** Apart from the
  7 words above, the word and phoneme counts agree TR by TR within boundary jitter in all 11
  stories.
- **This includes all of `life`.** The G-Node features cover its 430 kept TRs, so the transcript
  behind them includes the 71 s missing from the G-Node `.wav` file (section 3).
- **The semantic features agree less closely** (r about 0.93) than the counts. The release must
  build them in a way not reproduced here, for example a different normalisation of the word
  vectors. They support the word identity, but are not an exact test of it.

**Not verified:** the spelling of each word. The counts test the number and timing of the words;
only the semantic features depend on which words they are, and only for words in the english1000
vocabulary. A full word-by-word test would need a speech recogniser run on the audio.

## Changes

### 2026-10-09 11:35 — page created

New page recording where the Nature Stories TextGrids come from (OpenNeuro `ds003020`, a separate
release from the G-Node fMRI data), how the workflow uses them, and the check that both releases
describe the same stimuli, including the truncated G-Node `life` audio. Written on the developer's
request after the check was run.

### 2026-10-19 14:10 — word-level check added; three more non-speech labels removed

New section 4: the TextGrids were compared word count by word count with the per-TR features of the
G-Node release, with the new rule `check_nature_stories_textgrids`, which replaces the earlier note
that only durations had been compared. The check showed that `{cg}`, `{ig}` and `{sl}` labels were
reaching the transcripts; they were added to the non-speech labels in section 2. Section 2 also
records the two malformed labels that are still not removed.

### 2026-10-20 11:55 — check results saved to files

Rule `check_nature_stories_textgrids` used to print its tables only, so the numbers of section 4
existed only as a hand-copied table. It now writes `textgrid_check.tsv` and
`textgrid_check_unexplained_words.tsv` to `results/mind/nature_stories/qc/` and is built by
`all_nature_stories_dataset` (not by `rule all`). Section 4 gives the new command and the lowest
unrounded correlations. The values did not change.
