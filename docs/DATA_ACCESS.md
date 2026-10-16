# Data access and non-redistribution

This project uses MIMIC-IV v3.1 and eICU-CRD v2.0. The public repository does not include raw or row-level derived patient data.

Researchers must independently obtain access through PhysioNet and comply with the applicable credentialing, training, and data-use requirements.

The public scripts expect local files named:

- `data/restricted/BHR_MIMIC_analysis_ready.csv`
- `data/restricted/BHR_eICU_analysis_ready.csv`

These are study-specific analysis-ready exports derived from the credentialed databases. They must remain local and are excluded by `.gitignore`.

The repository may include aggregate metrics, fold-level hyperparameters, software provenance, and summary tables that do not permit reconstruction of patient-level records.
