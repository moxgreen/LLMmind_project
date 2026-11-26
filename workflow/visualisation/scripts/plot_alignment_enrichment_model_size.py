#!/usr/bin/env python3
# written with AI assistance: Claude Code, Claude Opus 5.5 (claude-opus-5-5)
# last AI edit: 2026-11-26, see docs/changelog/developers/ for details
import argparse

import matplotlib.pyplot as plt
import pandas as pd

from libraries.compute_alignment_enrichment import set_enrichment_y_scale
from libraries.manage_model_metadata import model_family, parse_model_parameters
from libraries.visualisation_utils import (
    add_null_line, 
    ALIGNMENT_ENRICHMENT_LABEL, 
    BRAIN_MODEL_ALIGNMENT_ENRICHMENT, 
    ENRICHMENT_NULL_LABEL, 
    MODEL_LEVEL, 
    plot_title, 
    save_figure, 
    STIMULI_TYPE_MARKERS, 
)

CONFIGURATION_COLUMNS = [
    "dataset", 
    "stimuli_type", 
    "similarity_type", 
    "number_of_neighbours", 
]
# families with two models give a within-family Spearman's rho of +1 or -1 by construction
MINIMUM_FAMILY_SIZE = 3
# one colour per family: the ten dark tab20 hues, then the light ones
FAMILY_COLOURMAP = "tab20"
FAMILY_COLOUR_ORDER = list(range(0, 20, 2)) + list(range(1, 20, 2))

def read_enrichments(path, parameters_by_model):
    # one row per (configuration, model): model-level enrichment = mean observed alignment
    # score / mean relabelled alignment score, as in compute_alignment_enrichment()
    summary = pd.read_csv(path, sep = "\t")
    enrichments = summary.pivot(
        index = CONFIGURATION_COLUMNS + ["model"], 
        columns = "statistic", 
        values = "value", 
    ).reset_index()
    enrichments["enrichment"] = (
        enrichments["observed_average_alignment_score"]
        /enrichments["empirical_null_mean_alignment_score"]
    )

    missing = sorted(set(enrichments["model"]) - set(parameters_by_model))

    if missing:
        raise ValueError(f"No number of parameters was provided for models {missing}")

    enrichments["parameters_millions"] = enrichments["model"].map(parameters_by_model)
    enrichments["family"] = enrichments["model"].map(model_family)

    return enrichments.sort_values(["family", "parameters_millions", "model"])

def plot_configuration(configuration, models, colour_by_family, plot_path):
    dataset, similarity_type, number_of_neighbours = configuration
    fig, ax = plt.subplots(figsize = (10, 7))

    # one line per family, its models in order of size, each point labelled with its model
    for (family, stimuli_type), family_models in models.groupby(
        ["family", "stimuli_type"]
    ):
        colour = colour_by_family[family]
        ax.plot(
            family_models["parameters_millions"], 
            family_models["enrichment"], 
            color = colour, 
            marker = STIMULI_TYPE_MARKERS[stimuli_type], 
            label = f"{family} ({stimuli_type})", 
        )

        for row in family_models.itertuples(index = False):
            ax.annotate(
                row.model, 
                (row.parameters_millions, row.enrichment), 
                xytext = (4, 4), 
                textcoords = "offset points", 
                fontsize = 7, 
                color = colour, 
            )

    add_null_line(ax, 1.0, ENRICHMENT_NULL_LABEL)
    ax.set_xscale("log")
    set_enrichment_y_scale(ax)
    ax.set_xlabel("Number of parameters (millions)")
    ax.set_ylabel(ALIGNMENT_ENRICHMENT_LABEL)
    ax.set_title(
        plot_title(
            MODEL_LEVEL, 
            f"{BRAIN_MODEL_ALIGNMENT_ENRICHMENT} by model size", 
            dataset, 
            similarity_type, 
            number_of_neighbours, 
        )
    )
    ax.legend(loc = "upper left", bbox_to_anchor = (1.01, 1.0), fontsize = 8)

    save_figure(fig, plot_path, model_figure = False)

def within_family_spearman(models):
    # Spearman's rho of enrichment against parameter count inside each family that has at
    # least MINIMUM_FAMILY_SIZE models, as the Pearson correlation of the ranks
    rows = []

    for family, family_models in models.groupby("family"):
        if len(family_models) < MINIMUM_FAMILY_SIZE:
            continue

        rows.append(
            {
                "family": family, 
                "number_of_models": len(family_models), 
                "spearman_rho": family_models["enrichment"].rank().corr(
                    family_models["parameters_millions"].rank()
                ), 
            }
        )

    return rows

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_level_statistics", 
                        required = True, 
                        help = "Whole-cortex TSV file containing model-level statistics")
    parser.add_argument("--model_parameters", 
                        nargs = "+", 
                        required = True, 
                        help = "Model parameter counts formatted as model=parameters_millions")
    parser.add_argument("--plot_pattern", 
                        required = True, 
                        help = "Plot path with {dataset}, {similarity_type} and {number_of_neighbours} placeholders")
    parser.add_argument("--within_family_spearman", 
                        required = True, 
                        help = "Output TSV file of the within-family Spearman's rho")
    args = parser.parse_args()

    # load the enrichments and give every family the same colour in every plot
    parameters_by_model = parse_model_parameters(args.model_parameters)
    enrichments = read_enrichments(args.model_level_statistics, parameters_by_model)
    colourmap = plt.get_cmap(FAMILY_COLOURMAP)
    colour_by_family = {
        family: colourmap(FAMILY_COLOUR_ORDER[index])
        for index, family in enumerate(
            sorted({model_family(model) for model in parameters_by_model})
        )
    }

    # plot each (dataset, similarity type, k) with every model of the dataset
    spearman_rows = []

    for configuration, models in enrichments.groupby(
        ["dataset", "similarity_type", "number_of_neighbours"]
    ):
        dataset, similarity_type, number_of_neighbours = configuration
        number_of_neighbours = int(number_of_neighbours)
        plot_configuration(
            (dataset, similarity_type, number_of_neighbours), 
            models, 
            colour_by_family, 
            args.plot_pattern.format(
                dataset = dataset, 
                similarity_type = similarity_type, 
                number_of_neighbours = number_of_neighbours, 
            ), 
        )

        for stimuli_type, stimuli_type_models in models.groupby("stimuli_type"):
            for row in within_family_spearman(stimuli_type_models):
                spearman_rows.append(
                    {
                        "dataset": dataset, 
                        "stimuli_type": stimuli_type, 
                        "similarity_type": similarity_type, 
                        "number_of_neighbours": number_of_neighbours, 
                        **row, 
                    }
                )

    # save the within-family Spearman's rho
    pd.DataFrame(spearman_rows).to_csv(
        args.within_family_spearman, 
        sep = "\t", 
        index = False, 
        float_format = "%.6g", 
    )

if __name__ == "__main__":
    main()
