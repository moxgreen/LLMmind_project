# written with AI assistance: Claude Code, Claude Opus 5.5 (claude-opus-5-5)
# last AI edit: 2026-11-26, see docs/changelog/developers/ for details

# the collaborator's test_narratives.py, step by step: the language models in the language
# region and in the whole cortex of Narratives, and a concept bootstrap of their difference
import argparse

import numpy as np
import pandas as pd

from libraries.compute_alignment import compute_alignment_scores
from libraries.compute_nearest_neighbours import (
    read_nearest_neighbours,
    read_stored_number_of_neighbours,
)

def load_neighbours(path):
    # the stored neighbours, read as stored, without duplicates and self-neighbours
    df = read_nearest_neighbours(path, read_stored_number_of_neighbours(path))
    df = df.drop_duplicates(subset = ["concept", "neighbour"])

    return df[df["concept"] != df["neighbour"]]

def restrict(df, concepts):
    return df[df["concept"].isin(concepts) & df["neighbour"].isin(concepts)]

def enrichment_matrix(model_neighbours, brain):
    # models x concepts: shared neighbours over the chance expectation k_model k_brain/(N - 1),
    # on the concepts of the first model file that the brain file also has
    models = [load_neighbours(path) for path in model_neighbours]
    concepts = np.intersect1d(models[0]["concept"].unique(), brain["concept"].unique())
    n = len(concepts)
    brain = restrict(brain, concepts)
    k_brain = brain.groupby("concept", observed = True).size().median()
    rows = []

    for model in models:
        model = restrict(model, concepts)
        k_model = model.groupby("concept", observed = True).size().median()
        common = compute_alignment_scores(model, brain, k_model)["common_neighbours"]
        rows.append(common.to_numpy()/(k_model*k_brain/(n - 1)))

    return np.vstack(rows), concepts

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--language_region",
                        required = True)
    parser.add_argument("--whole_cortex",
                        required = True)
    parser.add_argument("--model_neighbours",
                        nargs = "+",
                        required = True)
    parser.add_argument("--iterations",
                        type = int,
                        required = True)
    parser.add_argument("--seed",
                        type = int,
                        required = True)
    parser.add_argument("--regions",
                        required = True)
    args = parser.parse_args()

    # enrichment in each brain set, on the same concepts
    language, concepts = enrichment_matrix(
        args.model_neighbours,
        load_neighbours(args.language_region),
    )
    whole, whole_concepts = enrichment_matrix(
        args.model_neighbours,
        load_neighbours(args.whole_cortex),
    )

    if not np.array_equal(concepts, whole_concepts):
        raise ValueError(
            "The language region and the whole cortex have different concepts"
        )

    # median over models of the mean over concepts
    language_value = np.median(language.mean(axis = 1))
    whole_value = np.median(whole.mean(axis = 1))

    # concept bootstrap of the difference, with the collaborator's random stream
    rng = np.random.RandomState(args.seed)
    n = len(concepts)
    differences = np.zeros(args.iterations)

    for iteration in range(args.iterations):
        resample = rng.choice(n, n, replace = True)
        differences[iteration] = (
            np.median(language[:, resample].mean(axis = 1))
            - np.median(whole[:, resample].mean(axis = 1))
        )

    low, high = np.percentile(differences, [2.5, 97.5])
    pd.DataFrame(
        [
            {"quantity": "language region", "value": language_value},
            {"quantity": "whole cortex", "value": whole_value},
            {
                "quantity": "language region - whole cortex",
                "value": language_value - whole_value,
                "ci_low": low,
                "ci_high": high,
                "excludes_zero": bool(low*high > 0),
            },
        ]
    ).assign(concepts = n, models = len(language)).to_csv(
        args.regions,
        sep = "\t",
        index = False,
        float_format = "%.6g",
    )

if __name__ == "__main__":
    main()
