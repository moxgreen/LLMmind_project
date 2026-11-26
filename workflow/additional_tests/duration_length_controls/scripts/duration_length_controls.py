# written with AI assistance: Claude Code, Claude Opus 5.5 (claude-opus-5-5)
# last AI edit: 2026-11-26, see docs/changelog/developers/ for details
import argparse

import numpy as np
import pandas as pd

from libraries.compute_similarity import capped_embedding_matrix
from libraries.compute_statistics import (
    benjamini_hochberg,
    empirical_upper_tail_p_value,
)
from libraries.parquet_io import read_parquet
from libraries.relabelled_rsa import (
    brain_matrix,
    draw_permutations,
    read_published_spearman,
    relabelled_coefficients,
    require_published_coefficient,
    similarity_matrix,
    to_square,
    unit_ranks,
)

def stimulus_table(manifest_path, units, repetition_time):
    # per story: the scan length entering the ISC (its shortest file) and the subjects
    manifest = pd.read_csv(manifest_path, sep = "\t", dtype = {"subject": str})
    manifest["volumes"] = [
        np.load(path, mmap_mode = "r").shape[0]
        for path in manifest["parcel_ts"]
    ]
    table = manifest.groupby("task").agg(
        volumes = ("volumes", "min"),
        subjects = ("subject", "nunique"),
    ).loc[units]
    table["minutes"] = table["volumes"]*repetition_time/60

    return table

def residualise(values, covariate):
    # remove the linear effect of the covariate and rescale to unit norm
    residual = values - (values @ covariate)*covariate

    return residual/np.linalg.norm(residual)

def log_distance_ranks(values, rows, columns):
    # the similarity of two stories in a property: minus their absolute log difference
    log_values = np.log(values)

    return unit_ranks(-np.abs(np.subtract.outer(log_values, log_values))[rows, columns])

def p_value(null, observed):
    return empirical_upper_tail_p_value((null >= observed).sum(), len(null))

def analyse(
    dataset, 
    brain_embeddings, 
    manifest, 
    repetition_time, 
    frames, 
    published, 
    args, 
):
    # load the stories and their properties
    units, brain = brain_matrix(brain_embeddings)
    table = stimulus_table(manifest, units, repetition_time)
    table["mean_isc"] = brain.mean(axis = 1)
    table["mean_tokens"] = np.mean(
        [frame.loc[units, "n_tokens"].to_numpy() for frame in frames.values()],
        axis = 0,
    )
    size = len(units)
    rows, columns = np.triu_indices(size, k = 1)
    stream = draw_permutations(size, args.number_of_relabellings, args.random_seed)
    duration = log_distance_ranks(table["minutes"].to_numpy(), rows, columns)
    duration_square = to_square(duration, size, rows, columns)
    model_rows = []
    brain_rows = []

    for similarity_type in args.similarity_types:
        # does duration similarity predict the brain geometry?
        brain_similarity = similarity_matrix(brain, similarity_type)
        brain_ranks = unit_ranks(brain_similarity[rows, columns])
        observed = brain_ranks @ duration
        null = relabelled_coefficients(
            duration_square, 
            brain_ranks, 
            stream, 
            rows, 
            columns, 
        )
        brain_rows.append(
            {
                "dataset": dataset,
                "similarity_type": similarity_type,
                "brain_duration_rho": observed,
                "p": p_value(null, observed),
            }
        )

        for model, frame in frames.items():
            # the published RSA, and the model's own association with duration and tokens
            tokens = log_distance_ranks(
                frame.loc[units, "n_tokens"].to_numpy(dtype = float),
                rows,
                columns,
            )
            model_ranks = unit_ranks(
                similarity_matrix(
                    capped_embedding_matrix(frame, units),
                    similarity_type,
                )[rows, columns]
            )
            plain = brain_ranks @ model_ranks
            key = (dataset, similarity_type, model)
            require_published_coefficient(
                plain,
                published.loc[key, "observed_spearman_coefficient"],
                " ".join(key),
            )
            model_duration = model_ranks @ duration
            row = {
                "dataset": dataset,
                "similarity_type": similarity_type,
                "model": model,
                "rho": plain,
                "published_p": published.loc[key, "empirical_upper_tail_p_value"],
                "model_duration_rho": model_duration,
                "model_duration_p": p_value(
                    relabelled_coefficients(
                        duration_square,
                        model_ranks,
                        stream,
                        rows,
                        columns,
                    ),
                    model_duration,
                ),
                "model_tokens_rho": model_ranks @ tokens,
            }

            # partial RSA: the covariate removed from both rank vectors, model relabelled
            for name, covariate in {"duration": duration, "tokens": tokens}.items():
                brain_part = residualise(brain_ranks, covariate)
                model_part = residualise(model_ranks, covariate)
                partial = brain_part @ model_part
                row[f"partial_{name}_rho"] = partial
                row[f"partial_{name}_p"] = p_value(
                    relabelled_coefficients(
                        to_square(model_part, size, rows, columns),
                        brain_part,
                        stream,
                        rows,
                        columns,
                    ),
                    partial,
                )

            model_rows.append(row)

    models = pd.DataFrame(model_rows)

    for column in [
        "published_p",
        "model_duration_p",
        "partial_duration_p",
        "partial_tokens_p",
    ]:
        models[column[:-1] + "q"] = models.groupby("similarity_type")[column].transform(
            benjamini_hochberg
        )

    return table.assign(dataset = dataset), models, pd.DataFrame(brain_rows)

def mean_isc_associations(dataset, table, args):
    # two-sided permutation test of the Spearman correlation of mean ISC with each property
    stream = draw_permutations(
        len(table), 
        args.number_of_relabellings, 
        args.random_seed, 
    )
    target = unit_ranks(table["mean_isc"].to_numpy())
    properties = ["minutes", "mean_tokens"]
    rows = []

    # a dataset with the same subjects for every story has no subject-count association
    if table["subjects"].nunique() > 1:
        properties.append("subjects")

    for name in properties:
        source = unit_ranks(table[name].to_numpy())
        observed = target @ source
        null = source[stream] @ target
        rows.append(
            {
                "dataset": dataset,
                "property": name,
                "rho": observed,
                "p": p_value(np.abs(null), abs(observed) - 1e-12),
            }
        )

    return pd.DataFrame(rows)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--datasets",
                        nargs = "+",
                        required = True)
    parser.add_argument("--repetition_times",
                        nargs = "+",
                        type = float,
                        required = True)
    parser.add_argument("--brain_embeddings",
                        nargs = "+",
                        required = True)
    parser.add_argument("--manifests",
                        nargs = "+",
                        required = True)
    parser.add_argument("--models",
                        nargs = "+",
                        required = True)
    parser.add_argument("--model_embeddings",
                        nargs = "+",
                        required = True,
                        help = "one file per dataset and model, dataset-major")
    parser.add_argument("--spearman_summary",
                        required = True)
    parser.add_argument("--similarity_types",
                        nargs = "+",
                        required = True)
    parser.add_argument("--number_of_relabellings",
                        type = int,
                        required = True)
    parser.add_argument("--random_seed",
                        type = int,
                        required = True)
    parser.add_argument("--stimuli",
                        required = True)
    parser.add_argument("--models_output",
                        required = True)
    parser.add_argument("--brain_duration",
                        required = True)
    parser.add_argument("--mean_isc",
                        required = True)
    args = parser.parse_args()

    published = read_published_spearman(args.spearman_summary).set_index(
        ["dataset", "similarity_type", "model"]
    )
    outputs = {
        args.stimuli: [],
        args.models_output: [],
        args.brain_duration: [],
        args.mean_isc: [],
    }

    # analyse each dataset with its own models' embeddings
    for number, dataset in enumerate(args.datasets):
        paths = args.model_embeddings[
            number*len(args.models):(number + 1)*len(args.models)
        ]
        frames = {model: read_parquet(path) for model, path in zip(args.models, paths)}
        table, models, brain = analyse(
            dataset,
            args.brain_embeddings[number],
            args.manifests[number],
            args.repetition_times[number],
            frames,
            published,
            args,
        )

        for path, result in zip(
            outputs,
            [table, models, brain, mean_isc_associations(dataset, table, args)],
        ):
            outputs[path].append(result)

    # save one table per output, all datasets together
    outputs[args.stimuli] = [
        pd.concat(outputs[args.stimuli]).rename_axis("unit").reset_index()
    ]

    for path, results in outputs.items():
        pd.concat(results, ignore_index = True).to_csv(
            path,
            sep = "\t",
            index = False,
            float_format = "%.6g",
        )

if __name__ == "__main__":
    main()
