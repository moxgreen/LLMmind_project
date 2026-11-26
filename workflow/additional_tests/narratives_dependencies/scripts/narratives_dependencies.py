# written with AI assistance: Claude Code, Claude Opus 5.5 (claude-opus-5-5)
# last AI edit: 2026-11-26, see docs/changelog/developers/ for details
import argparse
from itertools import permutations, product

import numpy as np
import pandas as pd
from scipy.stats import rankdata

from libraries.compute_statistics import (
    benjamini_hochberg,
    empirical_upper_tail_p_value,
)
from libraries.relabelled_rsa import (
    brain_matrix,
    draw_permutations,
    model_matrix,
    read_published_spearman,
    relabelled_coefficients,
    require_published_coefficient,
    similarity_matrix,
    to_square,
    unit_ranks,
)

DATASET = "narratives"

def similarity_matrices(args):
    # the brain and model similarity matrices of every similarity type, on the brain's units
    units, brain = brain_matrix(args.brain_embeddings)
    model_matrices = {
        model: model_matrix(path, units)
        for model, path in zip(args.models, args.model_embeddings)
    }
    matrices = {}

    for similarity_type in args.similarity_types:
        matrices[similarity_type, "brain"] = similarity_matrix(brain, similarity_type)

        for model, matrix in model_matrices.items():
            matrices[similarity_type, model] = similarity_matrix(
                matrix,
                similarity_type,
            )

    return units, matrices

def pair_ranks(matrix, kept):
    rows, columns = np.triu_indices(len(kept), k = 1)

    return unit_ranks(matrix[np.ix_(kept, kept)][rows, columns])

def number_of_pairs(size):
    return size*(size - 1)//2

def test_units(matrices, kept, stream, args):
    # the published test (relabelling null, BH across the models) on the kept units
    rows, columns = np.triu_indices(len(kept), k = 1)
    results = []

    for similarity_type in args.similarity_types:
        brain = pair_ranks(matrices[similarity_type, "brain"], kept)
        coefficients = []
        p_values = []

        for model in args.models:
            ranks = pair_ranks(matrices[similarity_type, model], kept)
            coefficients.append(brain @ ranks)
            null = relabelled_coefficients(
                to_square(ranks, len(kept), rows, columns),
                brain,
                stream,
                rows,
                columns,
            )
            p_values.append(
                empirical_upper_tail_p_value(
                    (null >= coefficients[-1]).sum(),
                    len(stream),
                )
            )

        q_values = benjamini_hochberg(p_values)

        for model, rho, p, q in zip(args.models, coefficients, p_values, q_values):
            results.append(
                {
                    "similarity_type": similarity_type,
                    "model": model,
                    "rho": rho,
                    "q": q,
                }
            )

    return pd.DataFrame(results)

def summarise(tests, check, units):
    # one row per similarity type: the coefficients over models and the significant tests
    # (none when the check has no test)
    rows = []

    for similarity_type, group in tests.groupby("similarity_type", sort = False):
        tested = "q" in group
        rows.append(
            {
                "check": check,
                "similarity_type": similarity_type,
                "units": units,
                "pairs": number_of_pairs(units),
                "median_rho": group["rho"].median(),
                "minimum_rho": group["rho"].min(),
                "maximum_rho": group["rho"].max(),
                "tests": len(group) if tested else 0,
                "significant_tests": int((group["q"] < 0.05).sum()) if tested else 0,
            }
        )

    return rows

def leave_out_checks(units, matrices, blocks, args):
    # the RSA without single units and blocks, and with one unit per block
    position = {unit: i for i, unit in enumerate(units)}
    two_unit_blocks = [name for name, block in blocks.items() if len(block) == 2]
    exclusions = {"none": []}
    exclusions.update({unit: [unit] for unit in units})
    exclusions.update(blocks)
    exclusions[" + ".join(two_unit_blocks)] = [
        unit
        for name in two_unit_blocks
        for unit in blocks[name]
    ]
    rows = []

    for label, excluded in exclusions.items():
        kept = [position[unit] for unit in units if unit not in excluded]
        stream = draw_permutations(
            len(kept),
            args.number_of_relabellings,
            args.random_seed,
        )
        rows += summarise(
            test_units(matrices, kept, stream, args),
            f"without {label}",
            len(kept),
        )

    # one unit per block with the unrelated units, every combination
    subset_size = len(blocks) + len(args.unrelated_units)
    stream = draw_permutations(
        subset_size,
        args.number_of_relabellings,
        args.random_seed,
    )
    subsets = [
        test_units(
            matrices,
            [position[unit] for unit in list(chosen) + args.unrelated_units],
            stream,
            args,
        )
        for chosen in product(*blocks.values())
    ]
    rows += summarise(
        pd.concat(subsets, ignore_index = True),
        f"one unit per block ({len(subsets)} subsets)",
        subset_size,
    )

    # the coefficient without the pairs inside a block, with no test
    block_of = np.full(len(units), -1)

    for number, block in enumerate(blocks.values()):
        block_of[[position[unit] for unit in block]] = number

    rows_all, columns_all = np.triu_indices(len(units), k = 1)
    outside = (block_of[rows_all] != block_of[columns_all]) | (block_of[rows_all] < 0)
    coefficients = []

    for similarity_type, model in product(args.similarity_types, args.models):
        brain = matrices[similarity_type, "brain"][rows_all, columns_all][outside]
        values = matrices[similarity_type, model][rows_all, columns_all][outside]
        coefficients.append(
            {
                "similarity_type": similarity_type,
                "model": model,
                "rho": unit_ranks(brain) @ unit_ranks(values),
            }
        )

    without_block_pairs = summarise(
        pd.DataFrame(coefficients),
        "without the pairs inside a block",
        len(units),
    )

    for row in without_block_pairs:
        row["pairs"] = int(outside.sum())

    return pd.DataFrame(rows + without_block_pairs)

def restricted_stream(units, first_block, second_block, unrelated_units):
    # the unrelated units permuted among themselves, and the two 2-unit blocks swapped or
    # not (first_block[i] with second_block[i]); rows alternate unswapped and swapped
    position = {unit: i for i, unit in enumerate(units)}
    swap = {}

    for first, second in zip(first_block, second_block):
        swap[position[first]] = position[second]
        swap[position[second]] = position[first]

    unrelated = [position[unit] for unit in unrelated_units]
    stream = []

    for order, swapped in product(permutations(unrelated), [False, True]):
        permutation = np.arange(len(units))
        permutation[unrelated] = order

        if swapped:
            for source, target in swap.items():
                permutation[source] = target

        stream.append(permutation)

    return np.stack(stream)

def restricted_tests(units, matrices, blocks, full, published, args):
    rows, columns = np.triu_indices(len(units), k = 1)
    first_block, second_block = [block for block in blocks.values() if len(block) == 2]
    # which unit of one 2-unit block replaces which unit of the other is an arbitrary
    # choice, so both pairings are tested
    pairings = {
        f"{first_block[0]}-{second_order[0]}": second_order
        for second_order in [second_block, second_block[::-1]]
    }
    results = []

    for pairing, second_order in pairings.items():
        stream = restricted_stream(
            units,
            first_block,
            second_order,
            args.unrelated_units,
        )
        fixed_pairs = int(
            ((stream[:, rows] == rows) & (stream[:, columns] == columns))
            .all(axis = 0)
            .sum()
        )
        swapped = np.arange(len(stream))%2 == 1

        for similarity_type in args.similarity_types:
            brain = unit_ranks(matrices[similarity_type, "brain"][rows, columns])
            p_values = []
            diagnostics = []

            for model in args.models:
                ranks = unit_ranks(matrices[similarity_type, model][rows, columns])
                null = relabelled_coefficients(
                    to_square(ranks, len(units), rows, columns),
                    brain,
                    stream,
                    rows,
                    columns,
                )
                exceeds = null >= full[similarity_type, model] - 1e-12
                # the identity is in the set, so the exact p-value is the share at least as large
                p_values.append(exceeds.mean())
                diagnostics.append(
                    {
                        "unswapped_null_mean": null[~swapped].mean(),
                        "swapped_null_mean": null[swapped].mean(),
                        "unswapped_at_least_as_large": int(exceeds[~swapped].sum()),
                        "swapped_at_least_as_large": int(exceeds[swapped].sum()),
                    }
                )

            q_values = benjamini_hochberg(p_values)

            for model, p, q, diagnostic in zip(
                args.models,
                p_values,
                q_values,
                diagnostics,
            ):
                results.append(
                    {
                        "pairing": pairing,
                        "similarity_type": similarity_type,
                        "model": model,
                        "permutations": len(stream),
                        "fixed_pairs": fixed_pairs,
                        "rho": full[similarity_type, model],
                        "published_p": published.loc[
                            (similarity_type, model),
                            "empirical_upper_tail_p_value",
                        ],
                        "restricted_p": p,
                        "restricted_q": q,
                        **diagnostic,
                    }
                )

    return pd.DataFrame(results)

def unit_distinctness(units, matrices, args):
    # how far each unit sits from the others: the mean rank of its similarities, in the
    # brain and in the median model ranks
    rows, columns = np.triu_indices(len(units), k = 1)
    distinctness = pd.DataFrame(index = pd.Index(units, name = "unit"))

    for similarity_type in args.similarity_types:
        brain = rankdata(matrices[similarity_type, "brain"][rows, columns])
        model = np.median(
            [
                rankdata(matrices[similarity_type, name][rows, columns])
                for name in args.models
            ],
            axis = 0,
        )

        for source, values in {"brain": brain, "model": model}.items():
            distinctness[f"{similarity_type}_{source}"] = to_square(
                values,
                len(units),
                rows,
                columns,
            ).sum(axis = 1)/(len(units) - 1)

    return distinctness

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--brain_embeddings",
                        required = True)
    parser.add_argument("--models",
                        nargs = "+",
                        required = True)
    parser.add_argument("--model_embeddings",
                        nargs = "+",
                        required = True)
    parser.add_argument("--spearman_summary",
                        required = True)
    parser.add_argument("--unit_blocks",
                        nargs = "+",
                        required = True,
                        help = "name=unit,unit,... per block")
    parser.add_argument("--unrelated_units",
                        nargs = "+",
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
    parser.add_argument("--restricted_permutations",
                        required = True)
    parser.add_argument("--leave_out",
                        required = True)
    parser.add_argument("--unit_distinctness",
                        required = True)
    args = parser.parse_args()

    blocks = {
        name: units.split(",")
        for name, units in (block.split("=") for block in args.unit_blocks)
    }

    if [len(block) for block in blocks.values()].count(2) != 2:
        raise ValueError("The restricted permutations need exactly two 2-unit blocks")

    # load the matrices and check that the blocks cover every unit once
    units, matrices = similarity_matrices(args)
    named_units = [unit for block in blocks.values() for unit in block]

    if sorted(named_units + args.unrelated_units) != sorted(units):
        raise ValueError(
            "The blocks and unrelated units must list each of the "
            f"{len(units)} units once"
        )

    # check the full RSA against the published table
    table = read_published_spearman(args.spearman_summary)
    published = table[table["dataset"] == DATASET].set_index(
        ["similarity_type", "model"]
    )
    rows, columns = np.triu_indices(len(units), k = 1)
    full = {}

    for similarity_type, model in product(args.similarity_types, args.models):
        full[similarity_type, model] = (
            unit_ranks(matrices[similarity_type, "brain"][rows, columns])
            @ unit_ranks(matrices[similarity_type, model][rows, columns])
        )
        require_published_coefficient(
            full[similarity_type, model],
            published.loc[(similarity_type, model), "observed_spearman_coefficient"],
            f"{DATASET} {similarity_type} {model}",
        )

    # run the three checks and save them
    tables = {
        args.restricted_permutations: restricted_tests(
            units,
            matrices,
            blocks,
            full,
            published,
            args,
        ),
        args.leave_out: leave_out_checks(units, matrices, blocks, args),
    }

    for path, table in tables.items():
        table.to_csv(path, sep = "\t", index = False, float_format = "%.6g")

    unit_distinctness(units, matrices, args).to_csv(
        args.unit_distinctness,
        sep = "\t",
        float_format = "%.6g",
    )

if __name__ == "__main__":
    main()
