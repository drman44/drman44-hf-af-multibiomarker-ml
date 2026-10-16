# Validation report for public reproducibility release v1.1.1

The full repository was tested locally against the authors' credentialed analysis-ready MIMIC-IV/eICU files before packaging. Restricted row-level data were used only for local validation and are not included in the public release.

## Commands executed successfully

- `python scripts/01_build_modeling_cohorts.py`
  - MIMIC modeling cohort: N=3925, deaths=760
  - eICU modeling cohort: N=403, deaths=125
- `python scripts/02_validate_modeling_cohorts.py`
  - cohort size, event count, column-order and finite log-ratio gates passed
- `python scripts/04_external_validation.py`
  - locked XGBoost AUC 0.667626
  - Brier 0.203599
  - log loss 0.597357
  - clinical + raw components AUC 0.671626
- `python scripts/05_revision_analyses.py`
  - missingness, external dimensionality, calibration and component-comparison outputs generated
- `python scripts/05b_biomarker_completeness.py`
  - reviewer-requested completeness-selection outputs generated
- `python scripts/05c_imputation_sensitivity_reference.py`
  - canonical retained imputation-sensitivity output loaded successfully
- `pytest -q`
  - 3 tests passed

## Data-exclusion gate

No restricted row-level MIMIC-IV/eICU CSV, local output containing patient-level predictions, Python cache, or pytest cache is included in the public ZIP.
