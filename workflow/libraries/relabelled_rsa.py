# written with AI assistance: Claude Code, Claude Opus 5.5 (claude-opus-5-5)
# last AI edit: 2026-11-26, see docs/changelog/developers/ for details
import numpy as np
import pandas as pd
from scipy.stats import rankdata

from libraries.compute_similarity import (
    capped_embedding_matrix,
    dataframe_to_embedding_matrix,
    normalize_fn_for_similarity_type,
)
from libraries.parquet_io import read_parquet

# largest difference allowed between a recomputed and a published RSA coefficient
PUBLISHED_TOLERANCE = 1e-5

def similarity_matrix(embedding_matrix, similarity_type):
    normalised = normalize_fn_for_similarity_type(similarity_type)(embedding_matrix)

    return normalised @ normalised.T

def brain_matrix(path):
    # the concepts and the ISC matrix of an isc_dataframe.parquet file
    df = read_parquet(path)

    return df.index.to_numpy(), dataframe_to_embedding_matrix(df)

def model_matrix(path, concepts):
    # the capped embedding matrix of a model, as the Spearman RSA rule reads it
    return capped_embedding_matrix(read_parquet(path), concepts)

def unit_ranks(values):
    # centred ranks of unit norm: the dot product of two of them is Spearman's rho
    ranks = rankdata(values)
    ranks = ranks - ranks.mean()

    return ranks/np.linalg.norm(ranks)

def to_square(values, size, rows, columns):
    square = np.zeros((size, size))
    square[rows, columns] = values
    square[columns, rows] = values

    return square

def relabelled_coefficients(square, vector, permutations, rows, columns):
    # dot product of a vector with the relabelled matrix, one value per permutation
    return square[permutations[:, rows], permutations[:, columns]] @ vector

def draw_permutations(size, number_of_relabellings, random_seed):
    # the pipeline's relabelling stream
    rng = np.random.default_rng(random_seed)

    return np.stack([rng.permutation(size) for _ in range(number_of_relabellings)])

def read_published_spearman(path):
    # one row per (dataset, stimulus type, similarity, model) of the Spearman summary table
    return pd.read_csv(path, sep = "\t").pivot(
        index = ["dataset", "stimuli_type", "similarity_type", "model"],
        columns = "statistic",
        values = "value",
    ).reset_index()

def require_published_coefficient(coefficient, published, label):
    # the recomputed coefficient must match the pipeline before any variant is trusted
    if abs(coefficient - published) > PUBLISHED_TOLERANCE:
        raise ValueError(
            f"{label}: recomputed coefficient {coefficient} differs from the "
            f"published {published}"
        )
