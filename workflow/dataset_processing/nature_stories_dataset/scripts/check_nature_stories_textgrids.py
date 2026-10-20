# written with AI assistance: Claude Code, Claude Opus 5.5 (claude-opus-5-5)
# last AI edit: 2026-10-20, see docs/changelog/developers/ for details
"""
Check the Nature Stories TextGrids (OpenNeuro ds003020) against the words the
subjects heard, using the per-TR features that the G-Node release computed from
its own transcripts: rebuild the words and phonemes per TR, and the english1000
semantic features, from the TextGrids and correlate them with the released ones.
Write one row per story, and one row per TR whose words still differ.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import h5py

from convert_nature_stories_textgrids import (
    read_textgrid, 
    get_word_tier, 
    speech_entries, 
)

# TR of the Huth lab scans, in seconds
TR = 2.0045
# the first TR kept by the G-Node release starts 5 TRs after TextGrid time 0
TRIM_TRS = 5
# shift of the TR grid against the TextGrid times that matches the released
# word counts best (found empirically; the best value varies by about 10 ms per story)
TR_GRID_OFFSET = 0.01
# a +1 and a -1 word difference at most this many TRs apart are one word counted in
# a neighbouring TR by the other transcript
MAX_JITTER_TRS = 3

def counts_per_tr(times, n_trs):
    tr_index = np.floor((np.asarray(times) + TR_GRID_OFFSET)/TR).astype(int) - TRIM_TRS
    in_window = (tr_index >= 0) & (tr_index < n_trs)

    return tr_index, np.bincount(tr_index[in_window], minlength = n_trs)

def integer_counts(z_scored):
    # undo the z-scoring of a count feature, taking its smallest value as zero
    levels = np.unique(np.round(z_scored, 6))
    step = np.min(np.diff(levels))

    return np.round((z_scored - z_scored.min())/step).astype(int)

def unexplained_differences(differences):
    # cancel each difference against an opposite one in the next MAX_JITTER_TRS TRs
    differences = differences.copy()

    for i in range(len(differences)):
        for j in range(i + 1, min(i + 1 + MAX_JITTER_TRS, len(differences))):
            if differences[i]*differences[j] < 0:
                cancelled = min(abs(differences[i]), abs(differences[j]))
                differences[i] -= np.sign(differences[i])*cancelled
                differences[j] -= np.sign(differences[j])*cancelled

    return differences

def mean_column_correlation(rebuilt, released):
    return np.mean(
        [
            np.corrcoef(rebuilt[:, j], released[:, j])[0, 1]
            for j in range(rebuilt.shape[1])
            if rebuilt[:, j].std() > 0
        ]
    )

def main():
    parser = argparse.ArgumentParser(description = "Compare the Nature Stories TextGrids with the G-Node per-TR features.")
    parser.add_argument("--textgrids_dir", 
                        help = "Directory with one <story>.TextGrid per story.")
    parser.add_argument("--run_onsets", 
                        help = "Run onsets JSON giving each story's slice of the training features.")
    parser.add_argument("--features_matrix", 
                        help = "G-Node features_matrix.hdf.")
    parser.add_argument("--english1000", 
                        help = "G-Node english1000.hdf (semantic word vectors).")
    parser.add_argument("--output", 
                        help = "Output TSV with one row per story.")
    parser.add_argument("--unexplained_words", 
                        help = "Output TSV with one row per TR whose words still differ.")
    args = parser.parse_args()

    # load the released features and the english1000 word vectors
    run_metadata = json.loads(Path(args.run_onsets).read_text())
    features = h5py.File(args.features_matrix, "r")

    with h5py.File(args.english1000, "r") as f:
        word_vectors = f["data"][:]
        vocabulary = {
            word.decode(): i
            for i, word in enumerate(f["vocab"][:])
        }

    # each story's slice of the released features
    slices = [
        (story["story"], "train", story["onset"], story["length"])
        for story in run_metadata["train_stories"]
    ]
    slices.append((run_metadata["test_story"], "test", 0, run_metadata["test_trs"]))

    rows = [
        "story\tr_words\tsame_trs\tnet_word_difference\tunexplained_words\t"
        "r_phones\tr_semantic"
    ]
    flagged = ["story\ttr\tdifference\twords"]

    for story, split, onset, n_trs in slices:
        textgrid_file = Path(args.textgrids_dir)/f"{story}.TextGrid"
        tg = read_textgrid(textgrid_file)
        words = list(speech_entries(get_word_tier(tg, textgrid_file,)))
        phone_tier = next(
            tier
            for tier in tg["tiers"]
            if tier["name"] == "phone"
        )
        phone_times = [start for start, phone in speech_entries(phone_tier)]

        # words and phonemes per TR
        word_trs, word_counts = counts_per_tr([start for start, word in words], n_trs)
        _, phone_counts = counts_per_tr(phone_times, n_trs)
        released_words = integer_counts(
            features[f"numWords_{split}"][onset:onset + n_trs, 0]
        )
        released_phones = features[f"numPhone_{split}"][onset:onset + n_trs, 0]

        # word differences that are not a word counted in a neighbouring TR
        differences = unexplained_differences(word_counts - released_words)

        # sum of the english1000 vectors of the words in each TR
        semantic = np.zeros((n_trs, word_vectors.shape[0]))

        for tr, (start, word) in zip(word_trs, words):
            if 0 <= tr < n_trs and word in vocabulary:
                semantic[tr] += word_vectors[:, vocabulary[word]]

        released_semantic = features[f"semantic_{split}"][onset:onset + n_trs]

        rows.append(
            f"{story}\t"
            f"{np.corrcoef(word_counts, released_words)[0, 1]:.4f}\t"
            f"{np.mean(word_counts == released_words):.3f}\t"
            f"{np.sum(word_counts - released_words)}\t"
            f"{np.abs(differences).sum()}\t"
            f"{np.corrcoef(phone_counts, released_phones)[0, 1]:.4f}\t"
            f"{mean_column_correlation(semantic, released_semantic):.4f}"
        )

        for tr in np.flatnonzero(differences):
            tr_words = " ".join(
                word
                for word_tr, (start, word) in zip(word_trs, words)
                if word_tr == tr
            )
            flagged.append(f"{story}\t{tr}\t{differences[tr]:+d}\t{tr_words}")

    # save the per-story table and the TRs whose words differ (TextGrid minus G-Node)
    Path(args.output).write_text("\n".join(rows) + "\n")
    Path(args.unexplained_words).write_text("\n".join(flagged) + "\n")

if __name__ == "__main__":
    main()
