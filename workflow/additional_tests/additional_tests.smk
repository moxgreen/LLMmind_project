# written with AI assistance: Claude Code, Claude Opus 5.5 (claude-opus-5-5)
# last AI edit: 2026-11-26, see docs/changelog/developers/ for details

# definitions shared by the additional tests that read the main pipeline's outputs; included
# by each test's Snakefile after its configfile lines

shell.prefix(
    'export PYTHONPATH="$PWD/workflow:$PYTHONPATH"; '
)

# every test writes only below this folder
TESTS_DIR = "results/tests"

# the numeric environment of the main pipeline, relative to each test's Snakefile
ENVIRONMENT = "../../llm_mind_alignment/envs/llm_mind_alignment_environment.yaml"

SPEARMAN_SUMMARY = "results/tsv_summaries/all_spearman_alignment_scores.tsv"

def models_of(modality):
    return [
        model
        for model, model_config in config["models"].items()
        if model_config["modality"] == modality
    ]

LANGUAGE_MODELS = models_of("language")

def model_embeddings(dataset):
    return [
        f"results/language_models/{dataset}/embeddings/{model}_embeddings.parquet"
        for model in LANGUAGE_MODELS
    ]
