from pathlib import Path
import sys
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.common import calibration_parameters, patient_bootstrap_delta_auc, MODEL_FEATURES

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"outputs"
IN=ROOT/"data"/"restricted"
pred=pd.read_csv(OUT/"eICU_external_predictions_LOCAL_RESTRICTED.csv")
m=pd.read_csv(OUT/"MIMIC_modeling.csv")
e=pd.read_csv(OUT/"eICU_modeling.csv")

# Predictor missingness
cols=[c for c in m.columns if c!="outcome"]
missing=pd.DataFrame({
    "predictor":cols,
    "MIMIC_missing_n":[int(m[c].isna().sum()) for c in cols],
    "MIMIC_missing_pct":[100*m[c].isna().mean() for c in cols],
    "eICU_missing_n":[int(e[c].isna().sum()) for c in cols],
    "eICU_missing_pct":[100*e[c].isna().mean() for c in cols],
})
missing.to_csv(OUT/"reviewer_predictor_missingness.csv",index=False)

# External model dimensionality
cats=["sex","race","unit_type"]
features=dict(MODEL_FEATURES)
features["Locked XGBoost"]=[c for c in m.columns if c!="outcome"]
rows=[]
for name,fs in features.items():
    encoded=sum(int(m[c].dropna().nunique()) if c in cats else 1 for c in fs)
    rows.append([name,len(fs),encoded,125/len(fs),125/encoded])
pd.DataFrame(rows,columns=[
    "model","raw_predictor_count","post_encoding_input_columns",
    "external_events_per_raw_predictor_descriptive","external_events_per_encoded_column_descriptive"
]).to_csv(OUT/"reviewer_external_model_dimensionality.csv",index=False)

# External calibration CIs
def boot_cal(y,p,B=2000,seed=42):
    y=np.asarray(y,int); p=np.asarray(p,float); rng=np.random.default_rng(seed); n=len(y)
    vals=[]
    while len(vals)<B:
        idx=rng.integers(0,n,n); yy=y[idx]
        if yy.min()==yy.max(): continue
        vals.append(calibration_parameters(yy,p[idx]))
    vals=np.asarray(vals); point=np.asarray(calibration_parameters(y,p))
    lo,hi=np.quantile(vals,[.025,.975],axis=0)
    return point,lo,hi

cal=[]
for i,name in enumerate([c for c in pred.columns if c!="outcome"]):
    point,lo,hi=boot_cal(pred.outcome,pred[name],2000,42+i)
    cal.append([name,point[0],lo[0],hi[0],point[1],lo[1],hi[1],pred[name].mean(),pred.outcome.mean()])
pd.DataFrame(cal,columns=[
    "model","calibration_in_the_large","CITL_CI_low","CITL_CI_high",
    "calibration_slope","slope_CI_low","slope_CI_high","mean_predicted_risk","observed_risk"
]).to_csv(OUT/"reviewer_external_calibration_bootstrap.csv",index=False)

# Symmetric external comparator
point,lo,hi=patient_bootstrap_delta_auc(
    pred.outcome,pred["Clinical + raw components"],pred["Clinical base"],2000,42
)
pd.DataFrame([["Clinical + raw components vs Clinical base",point,lo,hi]],
             columns=["comparison","delta_AUC","CI_low","CI_high"]).to_csv(
                 OUT/"reviewer_component_vs_clinical_delta_auc.csv",index=False
             )

print("Reviewer-requested missingness, dimensionality, calibration and comparator outputs written.")
print("Biomarker-completeness and PMM-MICE sensitivity are implemented in the accompanying manuscript revision analysis package;")
print("they require the analysis-ready landmark files and statsmodels MICEData.")
