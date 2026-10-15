# Early multibiomarker machine-learning prediction in critically ill HF+AF

Reproducibility repository for:

**Early Multibiomarker Machine-Learning Prediction of In-Hospital Mortality in Critically Ill Patients With Heart Failure and Atrial Fibrillation**

Authors: Cevahir Alioglu, Nuray Kahraman Ay, Hasan Isleyen.

This repository contains the analysis code, locked model configuration, data-schema documentation, and non-patient-level reference outputs used for the Scientific Reports revision. **Restricted MIMIC-IV/eICU patient-level data are not redistributed.**

## What is reproducible here

The public code covers the complete path from locally obtained analysis-ready source files to:

1. the 6-hour complete-biomarker modeling cohorts;
2. conventional biomarker/component analyses;
3. leakage-protected model-development logic and stored fold-level tuning records;
4. locked XGBoost and unpenalized logistic comparator refits in MIMIC-IV;
5. unchanged external transport to eICU;
6. external AUC, Brier score, log loss, calibration, paired bootstrap comparisons, ablations, and risk distributions;
7. reviewer-requested missingness, imputation-sensitivity, model-dimensionality, and biomarker-completeness analyses.

The exact locked external XGBoost predictions and comparator predictions can be regenerated from the two local model-ready cohorts. On the authors' execution environment, the regenerated locked XGBoost metrics were AUC 0.667626, Brier 0.203599, and log loss 0.597357.

## Data are intentionally not included

MIMIC-IV and eICU-CRD are distributed through PhysioNet under their own credentialing/data-use requirements. Do **not** commit raw or derived row-level patient data to this repository.

Expected local input files:

```text
data/restricted/BHR_MIMIC_analysis_ready.csv
data/restricted/BHR_eICU_analysis_ready.csv
```

These filenames match the authors' analysis-ready exports. See `docs/DATA_ACCESS.md` and `docs/INPUT_SCHEMA.md`.

## Quick start

Create the exact environment where possible:

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Place the two restricted input CSVs under `data/restricted/`, then run:

```bash
python scripts/01_build_modeling_cohorts.py
python scripts/02_validate_modeling_cohorts.py
python scripts/04_external_validation.py
python scripts/05_revision_analyses.py
python scripts/05b_biomarker_completeness.py
python scripts/05c_imputation_sensitivity_reference.py
```

Optional internal-development replay/reference workflow:

```bash
python scripts/03_internal_validation_reference.py
```

Outputs are written to `outputs/`, which is git-ignored.

## Important provenance note

The retained execution artifacts record stage-specific random seeds:
- classical/revision/external stages: `42`;
- Phase-1 linear-model artifact: `20260804`;
- Phase-2 tree models and Phase-3 locked external validation: `42`.

The public code does not rewrite this provenance. See `docs/PROVENANCE.md`.

The surviving Phase-2 artifacts preserve selected fold-level hyperparameters and exact locked XGBoost/LightGBM candidate configurations. They do not preserve every losing Random Forest/Decision Tree candidate from the original inner-search grid. Therefore the public internal-development script is a transparent reference/replay implementation, while the **external locked-model pipeline is exactly specified and directly validated against the retained outputs**.

## Key scientific guardrails

- Predictor window: ICU admission through 6 hours.
- Landmark: 6 hours.
- Outcome: all-cause in-hospital mortality after the landmark.
- No post-landmark predictors in the primary model.
- MIMIC-IV used for development/model locking; eICU used only after lock.
- No eICU feature selection, hyperparameter tuning, coefficient refitting, or primary recalibration.
- Ratio-specific value is evaluated against the underlying lactate/BUN/hemoglobin components.
- SHAP describes model contribution, not causal importance.
- Decision-curve analysis is exploratory because external calibration was imperfect.

## Reference results

Non-patient-level reference results are in `reference_outputs/`. They are provided to audit a rerun without redistributing restricted patient-level predictions.

## Citation

See `CITATION.cff`. The Zenodo DOI should be added after the GitHub release is archived.

## License

No software license is asserted in this repository package. The authors should add their preferred open-source license before making the repository public if reuse beyond inspection/reproduction is intended.
