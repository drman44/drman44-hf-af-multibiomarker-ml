"""
Conventional association-analysis specification.

This script documents the exact primary adjustment sets used in the article. The retained canonical
pooled estimates are supplied in reference_outputs/classical_primary_association.csv.

The classical run used statsmodels MICEData predictive mean matching with 20 retained imputations;
for each imputation, logistic regression was fitted and coefficients/covariances pooled with Rubin's
rules. RCS knots and quartile cut points were derived in MIMIC and transferred unchanged to eICU.

This file is intentionally explicit about the estimand/adjustment sets and does not silently replace
the original PMM-MICE implementation with a different imputer.
"""
MODEL2=[
"age","sex","race","ckd","diabetes","hypertension","mi","cvd","copd","severe_liver","malignancy"
]
MODEL3=MODEL2+[
"unit_type","weight","sbp","dbp","heart_rate","resp_rate","platelet","wbc","rdw",
"glucose","creatinine","calcium","potassium","anion_gap"
]
EXPOSURES=["log2_lhr","log2_bhr"]
MICE_DRAWS=20
PMM_K=20
BURNIN=5
RCS_PERCENTILES=[0.05,0.35,0.65,0.95]
SUBGROUPS=["age","sex","ckd","anemia"]

if __name__=="__main__":
    print("Primary exposure models:")
    print("Model 1: exposure only")
    print("Model 2:",MODEL2)
    print("Model 3:",MODEL3)
    print("MICE draws:",MICE_DRAWS,"PMM k:",PMM_K,"burn-in:",BURNIN)
    print("See reference_outputs/classical_primary_association.csv for canonical pooled results.")
