# Analysis provenance

## Cohorts
- MIMIC-IV complete-biomarker development cohort: N=3925; deaths=760.
- eICU complete-biomarker external cohort: N=403; deaths=125.
- Predictor window: 0-6 h after ICU/unit admission.
- Landmark: 6 h.
- Primary outcome: all-cause in-hospital mortality after the landmark.

## Stage-specific execution records
The retained machine-readable artifacts record:
- Phase 1 linear models: Python 3.13.5; pandas 2.2.3; NumPy 2.3.5; scikit-learn 1.8.0; statsmodels 0.14.6; seed 20260804.
- Classical analyses: Python 3.13.5; pandas 2.2.3; NumPy 2.3.5; statsmodels 0.14.6; scikit-learn 1.8.0; SciPy 1.17.0; patsy 1.0.2.
- Phase 2 tree models: Python 3.13.5; scikit-learn 1.8.0; XGBoost 3.1.3; LightGBM 4.6.0; seed 42.
- Phase 3 external validation: Python 3.13.5; scikit-learn 1.8.0; XGBoost 3.1.3; seed 42.

The repository preserves these execution-time versions rather than replacing them with versions from a later environment.

## Lock
XGBoost was locked before eICU outcome evaluation using MIMIC only:
- n_estimators 180
- max_depth 3
- learning_rate 0.035
- subsample 0.90
- colsample_bytree 0.90
- reg_lambda 3.0

No eICU feature selection, hyperparameter tuning, coefficient refit, cutoff optimization, or primary recalibration was performed.

## Canonical Boruta note
The third-party Boruta package was not used. The reported analysis is a permutation shadow-feature stability procedure and must not be called canonical Boruta.
