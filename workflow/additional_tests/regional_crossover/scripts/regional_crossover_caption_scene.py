# written with AI assistance: Claude Code, Claude Opus 5.5 (claude-opus-5-5)
# last AI edit: 2026-11-26, see docs/changelog/developers/ for details

# the collaborator's test_caption_scene.py, step by step: vision and language models in the
# visual and language regions of Caption Scene (cells A-D), family medians of A and C, and a
# concept bootstrap of A - C and (A + D) - (B + C)
import argparse

import numpy as np
import pandas as pd

from libraries.compute_alignment import compute_alignment_scores
from libraries.compute_nearest_neighbours import (
    read_nearest_neighbours,
    read_stored_number_of_neighbours,
)
from libraries.manage_model_metadata import model_family

# the cells: (models, brain region)
CELLS = {
    "A": ("vision", "visual"),
    "B": ("vision", "language"),
    "C": ("language", "visual"),
    "D": ("language", "language"),
}

def load_neighbours(path):
    # the stored neighbours, read as stored, with the collaborator's diagnostics
    df = read_nearest_neighbours(path, read_stored_number_of_neighbours(path))
    df = df[["concept", "neighbour"]].astype(str)
    sizes = df.groupby("concept").size()
    diagnostics = {
        "duplicates": int(df.duplicated().sum()),
        "self": int((df["concept"] == df["neighbour"]).sum()),
        "k_min": int(sizes.min()),
        "k_max": int(sizes.max()),
        "concepts": int(sizes.size),
    }

    # the shared-neighbour count below uses sets, which equals the collaborator's merge
    # count only without duplicate rows
    if diagnostics["duplicates"]:
        raise ValueError(f"{path}: {diagnostics['duplicates']} duplicate rows")

    return df, diagnostics

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--visual_region",
                        required = True)
    parser.add_argument("--language_region",
                        required = True)
    parser.add_argument("--vision_models",
                        nargs = "+",
                        required = True)
    parser.add_argument("--vision_neighbours",
                        nargs = "+",
                        required = True)
    parser.add_argument("--language_models",
                        nargs = "+",
                        required = True)
    parser.add_argument("--language_neighbours",
                        nargs = "+",
                        required = True)
    parser.add_argument("--iterations",
                        type = int,
                        required = True)
    parser.add_argument("--seed",
                        type = int,
                        required = True)
    parser.add_argument("--cells",
                        required = True)
    parser.add_argument("--families",
                        required = True)
    args = parser.parse_args()

    # phase 1: diagnostics, no repairs
    brain = {}
    models = {}

    for region, path in {
        "visual": args.visual_region,
        "language": args.language_region,
    }.items():
        brain[region], diagnostics = load_neighbours(path)
        print(f"brain/{region}: {diagnostics}")

    for modality, names, paths in [
        ("vision", args.vision_models, args.vision_neighbours),
        ("language", args.language_models, args.language_neighbours),
    ]:
        models[modality] = {}

        for name, path in zip(names, paths):
            models[modality][name], diagnostics = load_neighbours(path)

            if diagnostics["k_min"] != diagnostics["k_max"]:
                raise ValueError(f"{name}: k is not uniform")

        print(f"models/{modality}: {len(names)} models")

    # phase 2: one universe of concepts, identical in every file
    tables = list(brain.values()) + [
        df
        for modality_models in models.values()
        for df in modality_models.values()
    ]
    universe = sorted(set.intersection(*[set(df["concept"]) for df in tables]))
    n = len(universe)

    for df in tables:
        concepts = set(df["concept"])
        neighbours = set(df["neighbour"])

        if concepts != set(universe) or not neighbours <= set(universe):
            raise ValueError("The concept sets differ between the neighbour files")

    k_brain = {
        region: int(df.groupby("concept").size().iloc[0])
        for region, df in brain.items()
    }
    print(f"N = {n}, brain k = {k_brain}")

    # phase 3: enrichment matrices, models x concepts
    def enrichment_matrix(modality, region):
        rows = []

        for name, df in models[modality].items():
            k_model = int(df.groupby("concept").size().iloc[0])
            common = compute_alignment_scores(df, brain[region], k_model)
            common = common["common_neighbours"]

            if common.sum() == 0:
                raise ValueError(f"{name} x {region}: no shared neighbours")

            rows.append(common.to_numpy()/(k_model*k_brain[region]/(n - 1)))

        return np.vstack(rows)

    enrichment = {cell: enrichment_matrix(*pairing) for cell, pairing in CELLS.items()}

    def cell_value(cell, concepts):
        # median over models of the mean enrichment over the concepts
        return np.median(enrichment[cell][:, concepts].mean(axis = 1))

    everything = np.arange(n)
    observed = {cell: cell_value(cell, everything) for cell in CELLS}
    contrasts = {
        "A - C": lambda values: values["A"] - values["C"],
        "(A + D) - (B + C)": lambda values: (
            values["A"] + values["D"] - values["B"] - values["C"]
        ),
    }

    # phase 4: families of A and C, with their numbers of models
    families = []

    for cell in ["A", "C"]:
        modality, region = CELLS[cell]
        table = pd.DataFrame(
            {
                "family": [model_family(name) for name in models[modality]],
                "enrichment": enrichment[cell].mean(axis = 1),
            }
        ).groupby("family")["enrichment"].agg(["median", "min", "max", "count"])
        families.append(
            table.sort_values("median", ascending = False)
            .reset_index()
            .assign(cell = cell, models = modality, brain_region = region)
        )

    pd.concat(families, ignore_index = True)[
        ["cell", "models", "brain_region", "family", "median", "min", "max", "count"]
    ].to_csv(args.families, sep = "\t", index = False, float_format = "%.6g")

    # phase 5: concept bootstrap of the contrasts
    rng = np.random.default_rng(args.seed)
    bootstrap = {label: np.empty(args.iterations) for label in contrasts}

    for iteration in range(args.iterations):
        concepts = rng.integers(0, n, n)
        values = {cell: cell_value(cell, concepts) for cell in CELLS}

        for label, contrast in contrasts.items():
            bootstrap[label][iteration] = contrast(values)

    rows = [
        {
            "quantity": cell,
            "models": modality,
            "brain_region": region,
            "value": observed[cell],
        }
        for cell, (modality, region) in CELLS.items()
    ]

    for label, contrast in contrasts.items():
        low, high = np.percentile(bootstrap[label], [2.5, 97.5])
        rows.append(
            {
                "quantity": label,
                "value": contrast(observed),
                "ci_low": low,
                "ci_high": high,
                "excludes_zero": bool(low*high > 0),
            }
        )

    pd.DataFrame(rows).to_csv(
        args.cells, 
        sep = "\t", 
        index = False, 
        float_format = "%.6g", 
    )

if __name__ == "__main__":
    main()
