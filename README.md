Reproducible computational evidence for Article 126.

Target journal: Computers and Geotechnics.

Public repository declared by the manuscript:
https://github.com/gabrielmontufar/article-126-internal-erosion-dem-fem/releases/tag/v1.0.4-cg-scope-fit-20260531

This package is a synthetic numerical-method benchmark and not an operational
dam-safety model.

Primary command for evaluators:

`python code/run_all_article_126_reproducibility.py`

Portable checksums are provided in `CHECKSUMS_SHA256.txt` using POSIX relative
paths with `/`.

This command rebuilds the complete local evidence set:

- `code/reproduce_article_126_clean.py`: legacy manufactured 1D verification, synthetic 2D screening benchmark, sensitivity, mesh check and Figures 1-5.
- `code/hybrid_dem_fem_graph_benchmark.py`: executable claim-code closure with a triangular 2D finite-element Darcy solver, Dijkstra lowest-cost path over cells and a bonded-particle DEM micro-window with bond breakage and homogenized return quantities.
- `code/external_validation_lee2021.py`: bounded external empirical challenge based on Lee, Kim and Chung (2021).
- `code/novelty_validation_scorecard.py`: novelty matrix against recent Computers and Geotechnics suffusion literature and bounded quantitative Lee et al. (2021) screening validation metrics.
- `code/external_ab_validation_baselines.py`: calibration subset A, held-out subset B and baseline comparison against critical-gradient, FEM-only, FEM-Dijkstra-without-DEM and simple empirical models.

The key file for addressing the strict MRNB claim-code objection is:

`data/hybrid_fem_dijkstra_dem_summary.json`

The key files for the MRNB novelty and validation/comparison criteria are:

- `data/novelty_matrix_cg_recent.csv`
- `data/lee2021_quantitative_screening_validation.csv`
- `data/lee2021_validation_metrics.csv`
- `data/novelty_validation_summary.json`
- `data/external_validation_ab_cases.csv`
- `data/external_validation_baseline_definitions.csv`
- `data/external_ab_validation_predictions.csv`
- `data/external_ab_validation_metrics.csv`
- `data/external_ab_validation_summary.json`
- `data/validation_levels_3_5_evidence.csv`
- `data/validation_editorial_sentence.txt`

Additional external challenge added for the Computers and Geotechnics revision:

- Run `python code/external_validation_lee2021.py`.
- It creates `data/external_lee2021_observations.csv`, `data/external_validation_challenge_results.csv`, and `data/external_validation_summary.json`.
- The source is Lee, Kim and Chung (2021), International Journal of Geo-Engineering, DOI 10.1186/s40703-021-00151-6.
- This is a bounded external empirical challenge. It supports the need for a path/history-sensitive screening indicator because published long-term suffusion occurred below short-term critical-gradient values. It is not quantitative field validation and must not be described as field-deployed operational dam-safety validation.

Versioned release for this submission: https://github.com/gabrielmontufar/article-126-internal-erosion-dem-fem/releases/tag/v1.0.4-cg-scope-fit-20260531



