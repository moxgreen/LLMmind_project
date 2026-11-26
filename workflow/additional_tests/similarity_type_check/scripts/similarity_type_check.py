# written with AI assistance: Claude Code, Claude Opus 5.5 (claude-opus-5-5)
# last AI edit: 2026-11-26, see docs/changelog/developers/ for details
import argparse

import numpy as np
import pandas as pd

from libraries.compute_isc import average_repeats_by_subject, compute_leave_one_out_isc
from libraries.compute_nearest_neighbours import (
    compute_blockwise_topk_from_embeddings,
    read_nearest_neighbours,
)
from libraries.compute_similarity import normalize_fn_for_similarity_type
from libraries.compute_statistics import (
    benjamini_hochberg,
    empirical_upper_tail_p_value,
)
from libraries.relabelled_rsa import brain_matrix, draw_permutations

# largest difference allowed between a recomputed and a published value
TOLERANCE = 1e-6

def model_neighbour_indices(path, concepts, number_of_neighbours):
    # the model's neighbours as a concepts x k array of concept positions
    position = {concept: i for i, concept in enumerate(concepts)}
    df = read_nearest_neighbours(path, number_of_neighbours)
    indices = np.full((len(concepts), number_of_neighbours), -1)

    for concept, group in df.groupby("concept", sort = False, observed = True):
        indices[position[concept]] = [
            position[neighbour]
            for neighbour in group["neighbour"]
        ]

    return indices

def score(isc, condition, draw, model_neighbours, relabelled, args):
    # the observed model-level alignment of every model and its relabelling p-value, with
    # the brain neighbours of this ISC
    n = len(isc)
    k = args.number_of_neighbours
    rows = []

    for similarity_type in args.similarity_types:
        brain_neighbours, _ = compute_blockwise_topk_from_embeddings(
            isc,
            k,
            normalize_fn_for_similarity_type(similarity_type),
        )
        mask = np.zeros((n, n), dtype = bool)
        mask[np.arange(n)[:, None], brain_neighbours] = True

        for model in args.models:
            key = (model, similarity_type)
            observed = mask[np.arange(n)[:, None], model_neighbours[key]].sum(axis = 1)
            observed = observed.mean()/k
            null = mask[np.arange(n)[None, :, None], relabelled[key]].sum(axis = 2)
            null = null.mean(axis = 1)/k
            rows.append(
                {
                    "condition": condition,
                    "draw": draw,
                    "similarity_type": similarity_type,
                    "model": model,
                    "observed": observed,
                    "p": empirical_upper_tail_p_value(
                        (null >= observed - 1e-12).sum(),
                        len(null),
                    ),
                }
            )

    return rows

def require_published(results, alignment_summary, number_of_neighbours):
    # the published condition must reproduce the pipeline's alignment and p-values
    published = pd.read_csv(alignment_summary, sep = "\t")
    published = published[
        (published["dataset"] == "narratives")
        & (published["number_of_neighbours"] == number_of_neighbours)
    ].pivot_table(
        index = ["similarity_type", "model"],
        columns = "statistic",
        values = "value",
        aggfunc = "first",
    )
    joined = results.set_index(["similarity_type", "model"]).join(published)

    for column, statistic in [
        ("observed", "observed_average_alignment_score"),
        ("p", "model_level_empirical_p_value"),
    ]:
        difference = (joined[column] - joined[statistic].astype(float)).abs().max()

        if difference > TOLERANCE:
            raise ValueError(
                f"The published condition differs from the pipeline's {statistic} "
                f"by up to {difference}"
            )

def story_arrays(manifest_path):
    # per story, the subjects' parcel time series truncated to the shortest run and with
    # repeated runs averaged, as the pipeline computes the ISC
    manifest = pd.read_csv(manifest_path, sep = "\t", dtype = {"subject": str})
    arrays_by_story = {}

    for task, group in manifest.groupby("task"):
        arrays = [np.load(path) for path in group["parcel_ts"]]
        shortest = min(array.shape[0] for array in arrays)
        arrays_by_story[task] = np.stack(
            average_repeats_by_subject(
                [array[:shortest] for array in arrays],
                group["subject"].tolist(),
            )
        ).astype(np.float32)

    return arrays_by_story

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--brain_embeddings",
                        required = True)
    parser.add_argument("--manifest",
                        required = True)
    parser.add_argument("--models",
                        nargs = "+",
                        required = True)
    parser.add_argument("--similarity_types",
                        nargs = "+",
                        required = True)
    parser.add_argument("--model_neighbours",
                        nargs = "+",
                        required = True,
                        help = "one file per similarity type and model, similarity-major")
    parser.add_argument("--alignment_summary",
                        required = True)
    parser.add_argument("--number_of_neighbours",
                        type = int,
                        required = True)
    parser.add_argument("--subsample_draws",
                        type = int,
                        required = True)
    parser.add_argument("--top_parcels",
                        type = int,
                        required = True)
    parser.add_argument("--log_offset",
                        type = float,
                        required = True)
    parser.add_argument("--number_of_relabellings",
                        type = int,
                        required = True)
    parser.add_argument("--random_seed",
                        type = int,
                        required = True)
    parser.add_argument("--summary",
                        required = True)
    parser.add_argument("--isc_properties",
                        required = True)
    args = parser.parse_args()

    # load the ISC and the model neighbours, and relabel the model neighbours with the
    # pipeline's permutation stream
    concepts, isc = brain_matrix(args.brain_embeddings)
    n = len(concepts)
    keys = [
        (model, similarity_type)
        for similarity_type in args.similarity_types
        for model in args.models
    ]
    model_neighbours = {
        key: model_neighbour_indices(path, concepts, args.number_of_neighbours)
        for key, path in zip(keys, args.model_neighbours)
    }
    permutations = draw_permutations(n, args.number_of_relabellings, args.random_seed)
    inverse = np.empty_like(permutations)
    inverse[np.arange(len(permutations))[:, None], permutations] = np.arange(n)
    relabelled = {
        key: inverse[
            np.arange(len(permutations))[:, None, None], 
            neighbours[permutations], 
        ]
        for key, neighbours in model_neighbours.items()
    }

    # published ISC, checked against the summary table
    rows = score(isc, "published", 0, model_neighbours, relabelled, args)
    require_published(
        pd.DataFrame(rows), 
        args.alignment_summary, 
        args.number_of_neighbours, 
    )

    # subject count: every story subsampled to the smallest story's subject count, from
    # an ISC recomputation checked against the published ISC
    arrays_by_story = story_arrays(args.manifest)
    recomputed = np.vstack(
        [compute_leave_one_out_isc(arrays_by_story[concept]) for concept in concepts]
    )

    if np.abs(recomputed - isc).max() > TOLERANCE:
        raise ValueError("The recomputed ISC differs from the published ISC")

    subsample_size = min(len(arrays) for arrays in arrays_by_story.values())
    draw_rng = np.random.default_rng(args.random_seed)

    for draw in range(args.subsample_draws):
        subsampled = np.vstack(
            [
                compute_leave_one_out_isc(
                    arrays_by_story[concept][
                        np.sort(
                            draw_rng.choice(
                                len(arrays_by_story[concept]),
                                subsample_size,
                                replace = False,
                            )
                        )
                    ]
                )
                for concept in concepts
            ]
        )
        rows += score(
            subsampled,
            f"subsampled_{subsample_size}",
            draw,
            model_neighbours,
            relabelled,
            args,
        )

    # skew: without the parcels of highest mean ISC, and log-transformed
    top = np.argsort(-isc.mean(axis = 0))[:args.top_parcels]
    rows += score(
        np.delete(isc, top, axis = 1),
        f"without_top_{args.top_parcels}",
        0,
        model_neighbours,
        relabelled,
        args,
    )
    rows += score(
        np.log(isc + args.log_offset),
        "log",
        0,
        model_neighbours,
        relabelled,
        args,
    )

    # models with p < 0.05 and q < 0.05 per draw, then their median and range over draws
    results = pd.DataFrame(rows)
    groups = ["condition", "draw", "similarity_type"]
    results["q"] = results.groupby(groups)["p"].transform(benjamini_hochberg)
    summary = (
        results.groupby(groups)
        .agg(
            median_observed = ("observed", "median"),
            p05 = ("p", lambda p: (p < 0.05).sum()),
            q05 = ("q", lambda q: (q < 0.05).sum()),
        )
        .reset_index()
        .groupby(["condition", "similarity_type"], sort = False)
        .agg(
            draws = ("draw", "size"),
            median_observed = ("median_observed", "median"),
            p05_median = ("p05", "median"),
            p05_min = ("p05", "min"),
            p05_max = ("p05", "max"),
            q05_median = ("q05", "median"),
            q05_min = ("q05", "min"),
            q05_max = ("q05", "max"),
        )
        .reset_index()
    )
    summary.to_csv(args.summary, sep = "\t", index = False, float_format = "%.6g")

    # the ISC properties behind the conditions: skew per story, the variance share of the
    # top parcels, and the values the log offset must lift
    centred = isc - isc.mean(axis = 1, keepdims = True)
    share = (centred[:, top]**2).sum(axis = 1)/(centred**2).sum(axis = 1)
    skewness = ((centred/isc.std(axis = 1, keepdims = True))**3).mean(axis = 1)
    log_skewness = pd.DataFrame(np.log(isc + args.log_offset)).skew(axis = 1)
    properties = {
        "median_skewness": np.median(skewness),
        "median_log_skewness": np.median(log_skewness),
        "median_top_parcel_variance_share": np.median(share),
        "top_parcel_label_ids": ",".join(str(i + 1) for i in np.sort(top)),
        "values_at_most_zero": int((isc <= 0).sum()),
        "number_of_values": isc.size,
        "smallest_value": isc.min(),
        "subsample_size": subsample_size,
    }
    pd.DataFrame(
        {"statistic": list(properties), "value": list(properties.values())}
    ).to_csv(args.isc_properties, sep = "\t", index = False)

if __name__ == "__main__":
    main()
