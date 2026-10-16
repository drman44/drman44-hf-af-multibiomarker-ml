"""
Reviewer-requested imputation sensitivity for the clinical + raw-components logistic comparator.

The canonical revision result is preserved in:
reference_outputs/revision_imputation_sensitivity.csv

Primary pipeline:
- MIMIC-trained median imputation for continuous variables;
- most-frequent categorical imputation;
- standardisation of numeric terms;
- effectively unpenalized logistic regression;
- unchanged transport to eICU.

Sensitivity:
- 20 outcome-blind predictive-mean-matching MICE draws;
- same raw-component comparator specification;
- predictions averaged across the 20 transported models;
- paired patient-level bootstrap for delta AUC.

Because stochastic MICE implementations can vary slightly with library/platform details, the canonical
revision result is the retained execution artifact:
AUC 0.6725 vs 0.6716 primary; delta AUC +0.0008
(95% CI -0.0025 to +0.0042).

This file is a method/provenance reference rather than a replacement of that retained artifact.
"""
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
ref=pd.read_csv(ROOT/"reference_outputs"/"revision_imputation_sensitivity.csv")
if __name__=="__main__":
    print(ref.to_string(index=False))
