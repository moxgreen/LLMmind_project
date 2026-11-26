# Study overview: design, data, models and where each part of the article is documented

> *Written with AI assistance (Claude Code). See [`docs/AI_USAGE.md`](../AI_USAGE.md).*

The pages in `docs/reference/` are the main source for the article that accompanies this code.
This page is their entry point: it summarises the study design, lists the datasets, models and
analysis parameters, says which page documents each part of the article, which numbers the
workflow and its additional tests reproduce and which come from one-off checks, and gathers the
limitations and the
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

### Terms used on these pages

- **Similarity** compares two stimuli *within* one representational space (the brain's, or one
  model's). **Alignment** compares two spaces: how alike they arrange the same stimuli.
- **Similarity type** (cosine, Pearson, Spearman) is how two stimuli's vectors are compared.
  **Spearman similarity** is one of these types; **Spearman RSA** (global alignment) is the
  Spearman correlation between two spaces' similarity structures, computed once for every
  similarity type. In code and output names the RSA is called `spearman_alignment`.
- **Concept-level** results and p-values describe one stimulus; **model-level** results and
  p-values describe one model (or model pair) over all stimuli. Only model-level p-values are
  tested and corrected for multiple testing ([`statistics.md`](statistics.md), sections 3 and 5).
- **ISC** measures how synchronised the subjects' BOLD time courses are for a stimulus, parcel by
  parcel. It is not the amplitude of the response ("activation"): a parcel can respond strongly
  with a low ISC if the response differs between subjects.
- **Language region** is the name of the 17-parcel region used for language models. It holds 8
  language and 9 auditory parcels ([`brain_regions.md`](brain_regions.md), section 2), so it is a
  combined language and auditory region, not a language-selective one. **Visual region** is the
  29-parcel `Vis` network.
- **Parameters** are total parameter counts. The Gemma 3n and Gemma 4 "E" models are named after
  their smaller *effective* counts (section 3).

## 2. Datasets

Counted from the workflow's manifests (`results/mind/<dataset>/manifests/`) on 2026-11-25, at
commit `da29acf`, with the current `config/config.yaml`. A "concept" is one stimulus that enters
the analysis.

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

38 models, 24 language and 14 vision, from `config/config.yaml` (`models:`) at commit
`da29acf`. All are loaded
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
- `results/tsv_summaries/model_size_within_family_spearman.tsv`, the model-size analysis
  ([`statistics.md`](statistics.md), section 8, "Model size");
- the figures under `results/pictures/` ([`statistics.md`](statistics.md), section 7).

Take result numbers from these tables, not from the pages: the pages quote some of them, at the
date given next to them.

**How to date a number on these pages.** The result tables and manifests are the authoritative
source; a number written on a page is a copy that can go out of date when the config, the
exclusion rules or the code change. Every such number carries the date it was measured, either
next to it or in the page's `## Changes` entry that added it. The code it was measured with is the
last commit before that date (`git log -1 --until=<date>`); the config is the one in that commit.
Numbers measured on the outputs of an earlier pipeline run say which run when it matters, as
[`clean_run_duration.md`](clean_run_duration.md) does. Before quoting a number in the article,
recompute it from the current tables or confirm that nothing it depends on has changed since its
date.

**Reproduced by the additional tests.** These analyses are outside the main pipeline, each with its
own Snakefile in `workflow/additional_tests/` and its tables in `results/tests/`; how to run them is
in the [additional-tests guide](../guides/additional_tests.md):

- the layer-depth pilot: 21 language models read at five relative depths on Narratives and Nature
  Stories, results in [`model_embeddings.md`](model_embeddings.md), "Layer-depth pilot results";
- the robustness checks of [`statistics.md`](statistics.md), section 8, except the model-size
  analysis (main pipeline): Narratives dependencies, duration and length, similarity types;
- the overlap of the NSD and Caption Scene images ([`fmri_preprocessing.md`](fmri_preprocessing.md));
- the regional crossover analysis ([`regional_crossover.md`](regional_crossover.md)).

**Not reproduced by the repository.** These numbers come from one-off checks, run once on the
workflow's outputs; no rule or script in the repository rebuilds them:

- the NSD trial-history figures (81% of preceding trials subject-specific; 178 of 1000 images with
  the same preceding trial in all subjects) in [`fmri_preprocessing.md`](fmri_preprocessing.md),
  "Limitation: the hemodynamic delay";
- the check of the Nature Stories corrected run onsets (README, "Input files that are not plain
  downloads"). The TextGrid word-level check, in contrast, is a workflow rule
  ([`nature_stories_stimuli.md`](nature_stories_stimuli.md), section 4).

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
- **Last layer only.** The main analysis reads every model at its last hidden state. In the
  layer-depth pilot, BLOOMZ, Gemma and Gemma 2 align better at intermediate depths and Gemma 3 and
  Gemma 4 at the last layer, so the last layer underestimates some families' alignment more than
  others ([`model_embeddings.md`](model_embeddings.md), "Layer-depth pilot results").
- **BOS token in the mean** of every language-model chunk. Removing it changes the neighbours
  slightly (89–100% shared) and no corrected significance ([`model_embeddings.md`](model_embeddings.md),
  "Measured effect of the BOS token").
- **Model size is confounded.** Within the Gemma 2, Gemma 3, Gemma 4 and OpenLLaMA families only
  the largest models are quantised; the families differ in training data, training objective
  (next-token prediction for the language models, of which BLOOMZ is also instruction-tuned;
  contrastive image-text learning for CLIP, three of them then fine-tuned on ImageNet-12k classification; self-supervised learning for DINOv2; supervised
  classification for the ImageNet-21k ViTs) and recipe; no language model is below 270M
  parameters; the "E" models count with their total parameters (section 3 above;
  [`statistics.md`](statistics.md), section 8, "Model size").
- **No noise ceiling.** How reliable the brain similarity structure is, and so the highest
  alignment any model could reach, was not estimated.
- **Group-level regions.** Both regions come from a group atlas, not from each subject; this fits
  individual language cortex poorly ([`brain_regions.md`](brain_regions.md), section 5).
- **Auditory parcels in the language region.** 9 of its 17 parcels are auditory, so on the spoken
  stories alignment there may reflect acoustic rather than linguistic processing
  ([`brain_regions.md`](brain_regions.md), section 2).
- **Ventral temporal cortex outside the visual region**, which is the 7-network `Vis` network
  ([`brain_regions.md`](brain_regions.md), section 5).
- **No cross-modality regional comparison in the workflow.** Each model is compared only with its
  own modality's region; the crossover analysis is an additional test outside the main pipeline
  ([`regional_crossover.md`](regional_crossover.md)).
- **Not every analysis is reproducible from the repository** (section 6).

## 8. References

The works cited on the reference pages. Entries marked † were checked on 2026-11-25 against the
publisher, Crossref, arXiv, Europe PMC or the release page. The note after an entry says what
could not be checked.

**Datasets**

- Nastase, S. A., Liu, Y.-F., Hillman, H., et al. (2021). The "Narratives" fMRI dataset for
  evaluating models of naturalistic language comprehension. *Scientific Data* 8, 250.
  doi:10.1038/s41597-021-01033-3 †
- Allen, E. J., St-Yves, G., Wu, Y., et al. (2022). A massive 7T fMRI dataset to bridge cognitive
  neuroscience and artificial intelligence. *Nature Neuroscience* 25(1), 116–126.
  doi:10.1038/s41593-021-00962-x †
- Li, S., Jin, Z., Gu, S., et al. (2026). A large-scale fMRI dataset for vision-language semantic
  association. *Scientific Data* 13, 905. doi:10.1038/s41597-026-07248-6 † (5 authors; the full
  list is in the Crossref record). Data: ScienceDB, doi:10.57760/sciencedb.27580.
- Huth, A. G., de Heer, W. A., Deniz, F., Gong, X. L. (2026). Nature story listening 3T fMRI data.
  G-Node GIN. doi:10.12751/g-node.t4wew2 †
- LeBel, A., Wagner, L., Jain, S., et al. (2023). A natural language fMRI dataset for voxelwise
  encoding models. *Scientific Data* 10, 555. doi:10.1038/s41597-023-02437-z † Data: OpenNeuro
  ds003020, doi:10.18112/openneuro.ds003020.v4.0.0.
- Lin, T.-Y., Maire, M., Belongie, S., et al. (2014). Microsoft COCO: Common objects in context.
  *ECCV 2014*, Lecture Notes in Computer Science 8693, 740–755. doi:10.1007/978-3-319-10602-1_48 †
  (the volume number 8693 was not in the Crossref record). Source of the NSD and Caption Scene
  images.

**Atlases and regions**

- Schaefer, A., Kong, R., Gordon, E. M., et al. (2018). Local-global parcellation of the human
  cerebral cortex from intrinsic functional connectivity MRI. *Cerebral Cortex* 28(9), 3095–3114.
  doi:10.1093/cercor/bhx179 †
- Kong, R., Yang, Q., Gordon, E., et al. (2021). Individual-specific areal-level parcellations
  improve functional connectivity prediction of behavior. *Cerebral Cortex* 31(10), 4477–4500.
  doi:10.1093/cercor/bhab101 † The CBIG repository calls the 17-network labels derived from it
  "Kong2022"; that these labels come from this paper was not checked.
- Fedorenko, E., Hsieh, P.-J., Nieto-Castañón, A., Whitfield-Gabrieli, S., Kanwisher, N. (2010).
  New method for fMRI investigations of language: defining ROIs functionally in individual
  subjects. *Journal of Neurophysiology* 104(2), 1177–1194. doi:10.1152/jn.00032.2010 †

**Models**

- Muennighoff, N., Wang, T., Sutawika, L., et al. (2023). Crosslingual generalization through
  multitask finetuning. *Proceedings of the 61st Annual Meeting of the ACL (Long Papers)*,
  15991–16111. doi:10.18653/v1/2023.acl-long.891 † (BLOOMZ)
- Gemma Team: Mesnard, T., Hardin, C., Dadashi, R., et al. (2024). Gemma: Open models based on
  Gemini research and technology. arXiv:2403.08295 †
- Gemma Team: Riviere, M., Pathak, S., Sessa, P. G., et al. (2024). Gemma 2: Improving open
  language models at a practical size. arXiv:2408.00118 †
- Gemma Team: Kamath, A., Ferret, J., Pathak, S., et al. (2025). Gemma 3 technical report.
  arXiv:2503.19786 †
- Gemma Team (2025). Gemma 3n. Google DeepMind. https://ai.google.dev/gemma/docs/gemma-3n † There
  is no technical report; this is the citation the Hugging Face model cards
  (`google/gemma-3n-E2B`, `google/gemma-3n-E4B`) ask for.
- Gemma Team: El Abd, S., Aggarwal, V., Algayres, R., et al. (2026). Gemma 4 technical report.
  arXiv:2607.02770 † (found in the arXiv listing and cited by the `google/gemma-4-*` model cards;
  the abstract page itself was not read).
- Geng, X., Liu, H. (2023). OpenLLaMA: An open reproduction of LLaMA. Software,
  https://github.com/openlm-research/open_llama † (the citation its README gives)
- Radford, A., Kim, J. W., Hallacy, C., et al. (2021). Learning transferable visual models from
  natural language supervision. *ICML 2021*, PMLR 139, 8748–8763. arXiv:2103.00020 † for the arXiv
  entry; the PMLR volume and pages come from a secondary source and were not checked. (CLIP)
- Cherti, M., Beaumont, R., Wightman, R., et al. (2023). Reproducible scaling laws for contrastive
  language-image learning. *CVPR 2023*, 2818–2829. doi:10.1109/CVPR52729.2023.00276 † (OpenCLIP
  models trained on LAION-2B)
- Schuhmann, C., Beaumont, R., Vencu, R., et al. (2022). LAION-5B: An open large-scale dataset for
  training next generation image-text models. *NeurIPS 2022 Datasets and Benchmarks Track*.
  arXiv:2210.08402 † (the dataset of which LAION-2B is the English part)
- Oquab, M., Darcet, T., Moutakanni, T., et al. (2024). DINOv2: Learning robust visual features
  without supervision. *Transactions on Machine Learning Research*. arXiv:2304.07193 † for the
  arXiv entry; the TMLR publication was not checked.
- Dosovitskiy, A., Beyer, L., Kolesnikov, A., et al. (2021). An image is worth 16x16 words:
  Transformers for image recognition at scale. *ICLR 2021*. arXiv:2010.11929 † (arXiv: "ICLR
  camera-ready version")
- Steiner, A., Kolesnikov, A., Zhai, X., Wightman, R., Uszkoreit, J., Beyer, L. (2022). How to
  train your ViT? Data, augmentation, and regularization in vision transformers. *Transactions on
  Machine Learning Research* (05/2022). arXiv:2106.10270 † (the `augreg_in21k` models)

**Methods compared with**

- Huh, M., Cheung, B., Wang, T., Isola, P. (2024). Position: The platonic representation
  hypothesis. *ICML 2024*. arXiv:2405.07987 † for the arXiv entry ("The Platonic Representation
  Hypothesis"); the ICML publication and its "Position:" title were not checked. (Value cap)
- Gröger, F., Wen, S., Brbić, M. (2026). Revisiting the platonic representation hypothesis: An
  Aristotelian view. *ICML 2026* (arXiv: "ICML 2026 camera-ready"). arXiv:2602.14486 † Its
  abstract matches what the pages cite it for: depth and width inflate representational
  similarity, a permutation-based null calibrates it, and local neighbourhood agreement survives
  calibration while global measures do not. That this is the paper the manuscript cites was not
  checked against the manuscript; Sec. 4.2 was not read.
- Antonello, R., Vaidya, A., Huth, A. (2023). Scaling laws for language encoding models in fMRI.
  *Advances in Neural Information Processing Systems 36 (NeurIPS 2023)*, 21895–21907.
  doi:10.52202/075280-0958, arXiv:2305.11863 †
- Caucheteux, C., King, J.-R. (2022). Brains and algorithms partially converge in natural language
  processing. *Communications Biology* 5, 134. doi:10.1038/s42003-022-03036-1 † (Author
  correction: *Communications Biology* 6, 396, 2023, doi:10.1038/s42003-023-04776-4.)

**Software**

- Mölder, F., Jablonski, K. P., Letcher, B., et al. (2021). Sustainable data analysis with
  Snakemake. *F1000Research* 10, 33. doi:10.12688/f1000research.29032.2 † (version 2)
- Avants, B. B., Tustison, N. J., Song, G., et al. (2011). A reproducible evaluation of ANTs
  similarity metric performance in brain image registration. *NeuroImage* 54(3), 2033–2044.
  doi:10.1016/j.neuroimage.2010.09.025 †
- Ciric, R., Thompson, W. H., Lorenz, R., et al. (2022). TemplateFlow: FAIR-sharing of
  multi-scale, multi-species brain models. *Nature Methods* 19, 1568–1571.
  doi:10.1038/s41592-022-01681-2 †
- Abraham, A., Pedregosa, F., Eickenberg, M., et al. (2014). Machine learning for neuroimaging
  with scikit-learn. *Frontiers in Neuroinformatics* 8, 14. doi:10.3389/fninf.2014.00014 †
  (nilearn)
- Wolf, T., Debut, L., Sanh, V., et al. (2020). Transformers: State-of-the-art natural language
  processing. *Proceedings of EMNLP 2020: System Demonstrations*, 38–45.
  doi:10.18653/v1/2020.emnlp-demos.6 †
- Wightman, R. (2019). PyTorch Image Models. GitHub,
  https://github.com/huggingface/pytorch-image-models. Not checked: the Zenodo DOI
  10.5281/zenodo.4414861 resolves to a 2023 release record (v0.8.10dev0), not to a 2019 entry;
  cite the version used (timm 1.0.30) or that record.
- Dettmers, T., Lewis, M., Belkada, Y., Zettlemoyer, L. (2022). LLM.int8(): 8-bit matrix
  multiplication for transformers at scale. *NeurIPS 2022*. arXiv:2208.07339 † (bitsandbytes
  8-bit)
- Dettmers, T., Pagnoni, A., Holtzman, A., Zettlemoyer, L. (2023). QLoRA: Efficient finetuning of
  quantized LLMs. *NeurIPS 2023*. arXiv:2305.14314 † for the arXiv entry; the NeurIPS publication
  was not checked. (bitsandbytes 4-bit)
- Gao, J. S., Huth, A. G., Lescroart, M. D., Gallant, J. L. (2015). Pycortex: an interactive
  surface visualizer for fMRI. *Frontiers in Neuroinformatics* 9, 23. doi:10.3389/fninf.2015.00023 †
  (Nature Stories' cortical voxels are defined with a pycortex mask)

## Changes

### 2026-11-25 12:00 — page created

New entry point for writing the article from the reference pages: study design, a dataset table
counted from the manifests, the model table from the config, analysis parameters and pinned
software versions, a map from article parts to pages, which numbers the workflow reproduces and
which come from one-off checks, the limitations, and a reference list.

### 2026-11-25 16:30 — layer-depth pilot finished; duplicated block removed

Section 6 no longer calls the layer-depth pilot "in progress" and points to its results; the
"Last layer only" limitation states what the pilot found. A block duplicated by an editing error
earlier the same day (the end of section 6, section 7 and the old reference list, repeated after
the new references) was removed.

### 2026-11-26 12:00 — additional tests

Section 6 gains a list of the analyses reproduced by the additional tests outside the main pipeline
(the layer-depth pilot, the robustness checks except model size, the image overlap and the
regional crossover), which were one-off checks until now; the remaining one-off checks are the
model-size analysis, the NSD trial-history figures and the check of the corrected Nature Stories
onsets. The limitation on cross-modality regional comparisons says the crossover is now an
additional test.

### 2026-11-26 14:45 — BOS token checked

The limitation about the BOS token now gives the result of the one-off check: removing the BOS
token changes no conclusion.

### 2026-11-26 17:30 — model-size analysis in the pipeline

Section 6: the model-size analysis is no longer a one-off check; the main pipeline writes its table
`model_size_within_family_spearman.tsv`, listed with the other workflow outputs.
