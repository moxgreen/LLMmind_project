# Study overview: design, data, models and where each part of the article is documented

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../AI_USAGE.md).*

The pages in `docs/reference/` are the main source for the article that accompanies this code.
This page is their entry point: it summarises the study design, lists the datasets, models and
analysis parameters, says which page documents each part of the article, which numbers the
workflow reproduces and which come from one-off checks, and gathers the limitations and the
references. Every fact that has a home on another page is only summarised here, with a link.

## 1. Study design

The study asks whether pretrained language and vision models organise naturalistic stimuli the
way the human brain does. For every stimulus (a story, an image, or a caption), the workflow
builds two representations:

- **brain:** a 200-value vector of leave-one-subject-out inter-subject correlation (ISC), one value
  per Schaefer parcel ([`fmri_preprocessing.md`](fmri_preprocessing.md));
- **model:** one embedding vector per model, mean-pooled over tokens for language models and the
  CLS token for vision models ([`model_embeddings.md`](model_embeddings.md)).

It then compares how the two spaces arrange the stimuli, under three similarity types (cosine,
Pearson, Spearman):

- **local alignment:** the share of each stimulus' *k* nearest neighbours that the brain and the
  model have in common, tested against a relabelling null;
- **global alignment (RSA):** the Spearman correlation between the brain's and the model's
  stimulus-by-stimulus similarities, tested against the same null.

Both are computed between brain and model, local alignment also between pairs of models, on the
whole cortex and on the region of the model's modality (language or visual,
[`brain_regions.md`](brain_regions.md)). The tests, multiple-testing rule and figures are in
[`statistics.md`](statistics.md).

## 2. Datasets

Counted from the workflow's manifests (`results/mind/<dataset>/manifests/`) on 2026-11-25. A
"concept" is one stimulus that enters the analysis.

| Dataset | Task | Stimuli given to the models | Concepts *n* | Subjects | TR | Time points per concept | *k* |
|---|---|---|---|---|---|---|---|
| Narratives | listening to spoken stories | transcripts | 18 stories | 324 (14–75 per story; 681 scans) | 1.5 s | the whole story | 5 |
| Nature Stories | listening to spoken stories | TextGrid word sequences | 11 stories | 11 (all hear every story) | 2.0 s | the whole story (291–430 TRs) | 3 |
| NSD | viewing natural images | images | 1000 images | 8 (all see every image, up to 3 times) | 1.333 s | 3 volumes (4 s) | 5, 25, 125 |
| Caption Scene | reading a caption, then viewing the image | captions (English translation) and images | 1000 images | 8 (all see every image, once or twice; mean 1.99) | 2.0 s | 6 volumes (12 s) | 5, 25, 125 |

- Which stimuli, runs and subjects are kept: [`fmri_preprocessing.md`](fmri_preprocessing.md),
  section 2, step 1.
- Public releases and their citations: the "Input data" section of the [README](../../README.md#input-data);
  the Nature Stories transcripts come from a separate release
  ([`nature_stories_stimuli.md`](nature_stories_stimuli.md)).
- The NSD and Caption Scene images share only 13 retained COCO images
  ([`fmri_preprocessing.md`](fmri_preprocessing.md), "Overlap between the Caption Scene and NSD
  images").
- *k* is a sensitivity analysis: every value is reported on its own, without correction across
  *k* ([`statistics.md`](statistics.md), section 5).

## 3. Models

38 models, 24 language and 14 vision, from `config/config.yaml` (`models:`). All are loaded
without their task head, from Hugging Face. "Parameters" is `parameters_millions` in the config,
the value used for ordering the figures and for the model-size analysis; for the Gemma 3n and
Gemma 4 "E" models it is the total, not the "effective" 2B or 4B of their names.

| Family | Models (parameters, millions) | Hugging Face IDs | Quantisation |
|---|---|---|---|
| BLOOMZ | 560M (560), 1.1B (1100), 1.7B (1700), 3B (3000), 7.1B (7100) | `bigscience/bloomz-*` | none |
| Gemma | 2B (2510), 7B (8540) | `google/gemma-2b`, `google/gemma-7b` | none |
| Gemma 2 | 2B (2600), 9B (9200), 27B (27200) | `google/gemma-2-{2b,9b,27b}` | 9B 8-bit, 27B 4-bit |
| Gemma 3 | 270M (270), 1B (1000), 4B (4300), 12B (12000), 27B (27000) | `google/gemma-3-270m`, `google/gemma-3-{1b,4b,12b,27b}-pt` | 12B 8-bit, 27B 4-bit |
| Gemma 3n | E2B (6000), E4B (8000) | `google/gemma-3n-{E2B,E4B}` | none |
| Gemma 4 | E2B (5100), E4B (8000), 12B (12000), 31B (31000) | `google/gemma-4-{E2B,E4B,12B,31B}` | 12B 8-bit, 31B 4-bit |
| OpenLLaMA | 3B (3000), 7B (7000), 13B (13000) | `openlm-research/open_llama_{3b,7b,13b}` | 13B 8-bit |
| CLIP (LAION-2B) | ViT-B/16 (86), ViT-L/14 (304), ViT-H/14 (632) | `timm/vit_{base_patch16,large_patch14,huge_patch14}_clip_224.laion2b` | none |
| CLIP (LAION-2B), ImageNet-12k fine-tuned | ViT-B/16 (86), ViT-L/14 (304), ViT-H/14 (632) | the same IDs with suffix `_ft_in12k` | none |
| DINOv2 | ViT-S/14 (22), ViT-B/14 (87), ViT-L/14 (304), ViT-g/14 (1100) | `facebook/dinov2-{small,base,large,giant}` | none |
| ViT, ImageNet-21k | Tiny/16 (6), Small/16 (22), Base/16 (86), Large/16 (307) | `timm/vit_{tiny,small,base,large}_patch16_224.augreg_in21k` | none |

The language models are base (pretrained) checkpoints, except BLOOMZ, which is instruction-tuned.
Quantisation (`bitsandbytes`) is used only so that the largest models fit on one 24 GB GPU.
How each model is loaded and read: [`model_embeddings.md`](model_embeddings.md).

## 4. Analysis parameters

| Parameter | Value | Described in |
|---|---|---|
| Brain atlas | Schaefer 2018, 200 parcels, 7 networks | [`fmri_preprocessing.md`](fmri_preprocessing.md), step 4 |
| Minimum subjects per stimulus | 2 (Nature Stories: all 11) | [`fmri_preprocessing.md`](fmri_preprocessing.md), step 1 |
| Regions | language 17 parcels, visual 29 parcels | [`brain_regions.md`](brain_regions.md), section 2 |
| Text chunks | at most 2048 tokens (BOS included), overlap 256 | [`model_embeddings.md`](model_embeddings.md), section 3 |
| Pooling | mean over tokens (language), CLS token (vision) | [`model_embeddings.md`](model_embeddings.md), sections 3–4 |
| Layer | last hidden state | [`model_embeddings.md`](model_embeddings.md), section 3 |
| Model-value cap | mean of each stimulus' 95th percentile of absolute values | [`model_embeddings.md`](model_embeddings.md), section 5 |
| Similarity types | cosine, Pearson, Spearman | [`statistics.md`](statistics.md), section 1 |
| Relabellings *N* | 10,000, one stream from seed 37 | [`statistics.md`](statistics.md), section 2 |
| Multiple testing | Benjamini-Hochberg per (dataset, similarity, *k*, statistic) | [`statistics.md`](statistics.md), section 5 |

Software, pinned in the workflow's conda environments (`workflow/**/envs/*.yaml`): Python 3.14.7,
Snakemake 9.27.0, PyTorch 2.13.0, transformers 5.18.0, timm 1.0.30, accelerate 1.15.0,
bitsandbytes 0.50.2, ANTs 2.6.5, nilearn 0.14.1, nibabel 5.4.2, NumPy 2.5.3, SciPy 1.18.1,
pandas 3.0.6, matplotlib 3.11.2, h5py 3.16.0, and `nsdcode` from GitHub (commit `bfd36a5`).
Hardware and run time: one NVIDIA RTX A5000 (24 GB); a clean run takes about 33 h
([`clean_run_duration.md`](clean_run_duration.md)).

## 5. Where each part of the article is documented

| Article part | Page and section |
|---|---|
| Datasets, fMRI preprocessing, ISC | [`fmri_preprocessing.md`](fmri_preprocessing.md); Nature Stories transcripts: [`nature_stories_stimuli.md`](nature_stories_stimuli.md) |
| Models and embeddings | section 3 above; [`model_embeddings.md`](model_embeddings.md) |
| Brain regions | [`brain_regions.md`](brain_regions.md) |
| Similarity, alignment score, null, tests, enrichment, RSA | [`statistics.md`](statistics.md), sections 1–6 |
| Figures and their conventions | [`statistics.md`](statistics.md), section 7 |
| Robustness checks (model size, Narratives dependencies, duration, similarity types) | [`statistics.md`](statistics.md), section 8 |
| Regional crossover (exploratory) | [`regional_crossover.md`](regional_crossover.md) |
| Limitations | section 7 below |
| Compute | [`clean_run_duration.md`](clean_run_duration.md) |

## 6. Where the numbers come from

**Reproduced by the workflow.** Every main result is written by `snakemake --use-conda` to:

- `results/tsv_summaries/all_model_brain_alignment_scores.tsv` (local alignment, brain-model),
  `all_model_model_alignment_scores.tsv` (model-model) and `all_spearman_alignment_scores.tsv`
  (RSA), each also with `_language` and `_vision` versions for the regions; their columns and
  which p-values are tests: [`statistics.md`](statistics.md), section 3;
- the figures under `results/pictures/` ([`statistics.md`](statistics.md), section 7).

Take result numbers from these tables, not from the pages: the pages quote some of them, at the
date given next to them.

**Not reproduced by the workflow.** These numbers come from one-off checks, run once on the
workflow's outputs; no rule or script in the repository rebuilds them:

- the robustness checks of [`statistics.md`](statistics.md), section 8, including the model-size
  analysis;
- the NSD trial-history figures (81% of preceding trials subject-specific; 178 of 1000 images with
  the same preceding trial in all subjects) in [`fmri_preprocessing.md`](fmri_preprocessing.md),
  "Limitation: the hemodynamic delay";
- the overlap of the NSD and Caption Scene images ([`fmri_preprocessing.md`](fmri_preprocessing.md));
- the regional crossover analysis ([`regional_crossover.md`](regional_crossover.md)), run with two
  scripts that are not in the repository;
- the check of the Nature Stories corrected run onsets (README, "Input files that are not plain
  downloads"). The TextGrid word-level check, in contrast, is a workflow rule
  ([`nature_stories_stimuli.md`](nature_stories_stimuli.md), section 4).

**In progress.** The layer-depth pilot reads a subset of the language models at several relative
depths ([`model_embeddings.md`](model_embeddings.md), "Which layer"); its results are not yet
documented on these pages.

## 7. Limitations

Each point is described in full on the page linked.

- **Short event windows and the hemodynamic delay.** NSD and Caption Scene ISCs are correlations
  over 3 and 6 volumes that start at stimulus onset; in NSD the window mostly holds the response
  to earlier trials ([`fmri_preprocessing.md`](fmri_preprocessing.md), "Limitation: the
  hemodynamic delay").
- **Few stories.** Narratives has 18 concepts and Nature Stories 11, so the nearest-neighbour
  scores are coarse and the null is discrete ([`statistics.md`](statistics.md), section 3).
- **The Narratives RSA rests on the two Shapes units.** Without them no model survives correction;
  the local alignment was not rechecked without them ([`statistics.md`](statistics.md), section 8,
  "Dependencies between the Narratives units").
- **The similarity type changes the Narratives result**, mostly through a few high-ISC auditory
  parcels ([`statistics.md`](statistics.md), section 8, "Why the similarity types differ on
  Narratives").
- **Last layer only.** Every model is read at its last hidden state, which may underestimate its
  alignment, unevenly across models ([`model_embeddings.md`](model_embeddings.md), "Which layer").
- **BOS token in the mean** of every language-model chunk
  ([`model_embeddings.md`](model_embeddings.md), "Caveat: the BOS token is included in the mean").
- **Model size is confounded.** Within the Gemma 2, Gemma 3, Gemma 4 and OpenLLaMA families only
  the largest models are quantised; the families differ in training data and recipe (BLOOMZ is
  instruction-tuned); no language model is below 270M parameters; the "E" models count with their
  total parameters (section 3 above; [`statistics.md`](statistics.md), section 8, "Model size").
- **No noise ceiling.** How reliable the brain similarity structure is, and so the highest
  alignment any model could reach, was not estimated.
- **Brain regions.** The language region comes from a group atlas, which fits individual language
  cortex poorly, and includes auditory parcels; the visual region excludes ventral temporal
  parcels; models are compared only with their own modality's region
  ([`brain_regions.md`](brain_regions.md), section 5).
- **Not every analysis is reproducible from the repository** (section 6).

## 8. References

The works cited on the reference pages. Entries marked † were checked against the publication;
the others were written from the pages and from memory and must be checked before submission.

**Datasets**

- Nastase, S. A., Liu, Y.-F., Hillman, H., et al. (2021). The "Narratives" fMRI dataset for
  evaluating models of naturalistic language comprehension. *Scientific Data* 8, 250.
  doi:10.1038/s41597-021-01033-3 †
- Allen, E. J., et al. (2022). A massive 7T fMRI dataset to bridge cognitive neuroscience and
  artificial intelligence. *Nature Neuroscience* 25, 116–126.
- Li et al. (2026). A large-scale fMRI dataset for vision-language semantic association (Caption
  Scene Dataset). *Scientific Data*. doi:10.1038/s41597-026-07248-6; data: ScienceDB
  doi:10.57760/sciencedb.27580.
- Huth, A. G., de Heer, W. A., Deniz, F., Gong, X., Gallant, J. L., Theunissen, F. E. Nature story
  listening 3T fMRI data. G-Node GIN, doi:10.12751/g-node.t4wew2.
- LeBel, A., Wagner, L., Jain, S., et al. (2023). A natural language fMRI dataset for voxelwise
  encoding models. *Scientific Data* 10, 555. Data: OpenNeuro ds003020,
  doi:10.18112/openneuro.ds003020.v4.0.0.
- Lin, T.-Y., et al. (2014). Microsoft COCO: Common objects in context. *ECCV 2014*. (Source of the
  NSD and Caption Scene images.)

**Atlases and regions**

- Schaefer, A., et al. (2018). Local-global parcellation of the human cerebral cortex from
  intrinsic functional connectivity MRI. *Cerebral Cortex* 28, 3095–3114.
- Kong, R., et al. (2021). Individual-specific areal-level parcellations improve functional
  connectivity prediction of behavior. *Cerebral Cortex* 31, 4477–4500. (The "Kong2022" 17-network
  labels of the Schaefer parcellation in the CBIG repository.)
- Fedorenko, E., Hsieh, P.-J., Nieto-Castañón, A., Whitfield-Gabrieli, S., Kanwisher, N. (2010).
  New method for fMRI investigations of language: defining ROIs functionally in individual
  subjects. *Journal of Neurophysiology* 104, 1177–1194. doi:10.1152/jn.00032.2010

**Models**

- Muennighoff, N., et al. (2023). Crosslingual generalization through multitask finetuning.
  *ACL 2023*. (BLOOMZ)
- Gemma Team (2024). Gemma: Open models based on Gemini research and technology. arXiv:2403.08295.
- Gemma Team (2024). Gemma 2: Improving open language models at a practical size.
  arXiv:2408.00118.
- Gemma Team (2025). Gemma 3 technical report. arXiv:2503.19786.
- Gemma 3n and Gemma 4: no reference recorded; cite the Hugging Face model cards.
- Geng, X., Liu, H. (2023). OpenLLaMA: An open reproduction of LLaMA. Software,
  github.com/openlm-research/open_llama.
- Radford, A., et al. (2021). Learning transferable visual models from natural language
  supervision. *ICML 2021*. (CLIP)
- Cherti, M., et al. (2023). Reproducible scaling laws for contrastive language-image learning.
  *CVPR 2023*. (OpenCLIP models trained on LAION-2B)
- Oquab, M., et al. (2024). DINOv2: Learning robust visual features without supervision.
  *Transactions on Machine Learning Research*.
- Dosovitskiy, A., et al. (2021). An image is worth 16x16 words: Transformers for image
  recognition at scale. *ICLR 2021*.
- Steiner, A., et al. (2022). How to train your ViT? Data, augmentation, and regularization in
  vision transformers. *Transactions on Machine Learning Research*. (The `augreg_in21k` models)

**Methods compared with**

- Huh, M., Cheung, B., Wang, T., Isola, P. (2024). Position: The platonic representation
  hypothesis. *ICML 2024*. (Value cap, layer choice)
- Antonello, R. J., Vaidya, A. R., Huth, A. G. (2023). Scaling laws for language encoding models
  in fMRI. arXiv:2305.11863 (NeurIPS 2023). †
- Caucheteux, C., King, J.-R. (2022). Brains and algorithms partially converge in natural language
  processing. *Communications Biology* 5, 134. doi:10.1038/s42003-022-03036-1
- Gröger et al.: cited by [`model_embeddings.md`](model_embeddings.md) and the manuscript for
  local versus global alignment and the best-of-many-layers bias; the full reference is not
  recorded in the repository.

**Software**

- Mölder, F., et al. (2021). Sustainable data analysis with Snakemake. *F1000Research* 10, 33.
- Avants, B. B., et al. (2011). A reproducible evaluation of ANTs similarity metric performance in
  brain image registration. *NeuroImage* 54, 2033–2044.
- Ciric, R., et al. (2022). TemplateFlow: FAIR-sharing of multi-scale, multi-species brain models.
  *Nature Methods* 19, 1568–1571.
- Abraham, A., et al. (2014). Machine learning for neuroimaging with scikit-learn. *Frontiers in
  Neuroinformatics* 8, 14. (nilearn)
- Wolf, T., et al. (2020). Transformers: State-of-the-art natural language processing.
  *EMNLP 2020: System Demonstrations*.
- Wightman, R. (2019). PyTorch Image Models (timm). Software, github.com/huggingface/pytorch-image-models.
- Dettmers, T., et al. (2022). LLM.int8(): 8-bit matrix multiplication for transformers at scale.
  *NeurIPS 2022*; Dettmers, T., et al. (2023). QLoRA: Efficient finetuning of quantized LLMs.
  *NeurIPS 2023*. (bitsandbytes 8-bit and 4-bit)
- Gao, J. S., Huth, A. G., Lescroart, M. D., Gallant, J. L. (2015). Pycortex: an interactive
  surface visualizer for fMRI. *Frontiers in Neuroinformatics* 9, 23. (Nature Stories' cortical voxels are defined with a
  pycortex mask)

## Changes

### 2026-11-25 12:00 — page created

New entry point for writing the article from the reference pages: study design, a dataset table
counted from the manifests, the model table from the config, analysis parameters and pinned
software versions, a map from article parts to pages, which numbers the workflow reproduces and
which come from one-off checks, the limitations, and a reference list.
