# Early Multibiomarker Machine-Learning Prediction of In-Hospital Mortality in Critically Ill Patients With Heart Failure and Atrial Fibrillation

**Authors:** Cevahir Alioglu, MD; Nuray Kahraman Ay, MD; Hasan Isleyen, MD  
**Affiliation:** Department of Cardiology, Bezmialem Vakif University Faculty of Medicine, Istanbul, Turkey  
**Corresponding author:** Hasan Isleyen, MD (`hasanburak.isleyen@nisantasi.edu.tr`)

This is the **full reproducibility release (v1.1.0)** for the Scientific Reports revision. It contains executable analysis code, locked model configuration, data-schema documentation, software provenance, tests, and non-patient-level reference outputs. Restricted MIMIC-IV/eICU row-level data and patient-level predictions are not redistributed.

## Study design

- Development: MIMIC-IV v3.1; N=3,925; 760 post-landmark in-hospital deaths.
- External validation: eICU-CRD v2.0; N=403; 125 post-landmark in-hospital deaths.
- Time zero: ICU admission.
- Predictor window: 0-6 hours.
- Landmark: 6 hours; deaths/discharges at or before the landmark excluded.
- Outcome: all-cause in-hospital mortality after the landmark.
- External model: selected/locked using MIMIC only, then transported unchanged to eICU.

## Public release contents

```text
scripts/
  01_build_modeling_cohorts.py
  02_validate_modeling_cohorts.py
  03_internal_validation_reference.py
  04_external_validation.py
  05_revision_analyses.py
  05b_biomarker_completeness.py
  05c_imputation_sensitivity_reference.py
  06_classical_analysis_specification.py

src/
  common.py

tests/
  test_core.py

docs/
  DATA_ACCESS.md
  INPUT_SCHEMA.md
  PROVENANCE.md
  VALIDATION_REPORT.md

config/
  analysis_config.json
  input_schema.json
  locked_xgboost_config.json
  software_provenance.json

reference_outputs/
  non-patient-level audit/reference outputs
```

`PUBLIC_RELEASE_FILELIST.txt` is generated from the actual repository contents.

## Restricted data

Researchers must obtain MIMIC-IV and eICU-CRD independently through PhysioNet and comply with the applicable credentialing and data-use requirements. Do not commit restricted row-level data.

Expected local files:

```text
data/restricted/BHR_MIMIC_analysis_ready.csv
data/restricted/BHR_eICU_analysis_ready.csv
```

The `data/restricted/` directory is protected by `.gitignore`.

## Exact environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The execution-time environment is also documented in `environment.yml` and `config/software_provenance.json`.

## Reproduce the locked external validation

```bash
python scripts/01_build_modeling_cohorts.py
python scripts/02_validate_modeling_cohorts.py
python scripts/04_external_validation.py
python scripts/05_revision_analyses.py
python scripts/05b_biomarker_completeness.py
python scripts/05c_imputation_sensitivity_reference.py
pytest -q
```

The locked external validation reproduces:

- XGBoost AUC 0.667626
- Brier score 0.203599
- log loss 0.597357
- clinical + raw-component logistic AUC 0.671626

The external validation is unchanged transport: no eICU feature selection, hyperparameter tuning, coefficient refit, cutoff optimization, or primary recalibration.

## Important provenance note

Stage-specific retained seeds are preserved rather than rewritten:

- classical/revision/external analyses: 42;
- Phase-1 linear-model execution record: 20260804;
- Phase-2 tree and Phase-3 external validation: 42.

The shadow-feature procedure is Boruta-inspired but **not canonical Boruta**.

## Validation

See `docs/VALIDATION_REPORT.md`. The public pipeline was rerun against the authors' local credentialed analysis-ready files before packaging; restricted data are not included in this release.

## Zenodo archive

After pushing this full repository to GitHub, create a GitHub release/tag (recommended `v1.1.0`) and let the Zenodo GitHub integration archive that release. Use the **new version DOI generated for this full-code release** in the manuscript and response letter.

The earlier partial archive should not be used as the code citation for the revised manuscript.

## License

MIT License. See `LICENSE`.
