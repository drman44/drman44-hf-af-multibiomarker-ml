from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.special import expit, logit
from sklearn.metrics import roc_auc_score

MODEL_COLUMNS = [
    "outcome","age","sex","race","unit_type","weight","sbp","dbp","heart_rate","resp_rate",
    "platelet","wbc","rbc","rdw","glucose","creatinine","calcium","potassium","anion_gap",
    "hemoglobin","log2_lactate","log2_bun","log2_lhr","log2_bhr","mi","pvd","cvd","copd",
    "rheumatic","pud","diabetes","ckd","malignancy","severe_liver","hypertension","anemia"
]
CATEGORICAL = ["sex","race","unit_type"]
CLINICAL = [
    "age","sex","race","unit_type","weight","sbp","dbp","heart_rate","resp_rate",
    "mi","pvd","cvd","copd","rheumatic","pud","diabetes","ckd","malignancy",
    "severe_liver","hypertension","anemia"
]
EXTENDED_LABS = ["platelet","wbc","rbc","rdw","glucose","creatinine","calcium","potassium","anion_gap"]

MODEL_FEATURES = {
    "Clinical base": CLINICAL,
    "Clinical + LHR": CLINICAL + ["log2_lhr"],
    "Clinical + BHR": CLINICAL + ["log2_bhr"],
    "Clinical + LHR + BHR": CLINICAL + ["log2_lhr","log2_bhr"],
    "Clinical + raw components": CLINICAL + ["log2_lactate","log2_bun","hemoglobin"],
    "Clinical + all early labs": CLINICAL + ["log2_lactate","log2_bun","hemoglobin"] + EXTENDED_LABS,
}

def collapse_mimic_race(x):
    if pd.isna(x): return "Other/Unknown"
    s=str(x).upper()
    if "PORTUGUESE" in s or "WHITE" in s: return "White"
    if "BLACK" in s: return "Black"
    if "ASIAN" in s: return "Asian"
    if "HISPANIC" in s or "LATINO" in s: return "Hispanic"
    return "Other/Unknown"

def collapse_eicu_race(x):
    if pd.isna(x): return "Other/Unknown"
    s=str(x)
    if s == "Caucasian": return "White"
    if s == "African American": return "Black"
    if s == "Asian": return "Asian"
    if s == "Hispanic": return "Hispanic"
    return "Other/Unknown"

def collapse_mimic_unit(x):
    if pd.isna(x): return "Medical"
    s=str(x)
    if s in {"Coronary Care Unit (CCU)","Cardiac Vascular Intensive Care Unit (CVICU)"}:
        return "Cardiac"
    if s in {"Medical Intensive Care Unit (MICU)","Medical/Surgical Intensive Care Unit (MICU/SICU)","Medicine"}:
        return "Medical"
    if s in {"Neuro Intermediate","Neuro Stepdown"}:
        return "Neuro"
    return "Surgical/Trauma"

def collapse_eicu_unit(x):
    if pd.isna(x): return "Medical"
    s=str(x)
    if s in {"Cardiac ICU","CCU-CTICU","CTICU","CSICU"}: return "Cardiac"
    if s in {"Med-Surg ICU","MICU"}: return "Medical"
    if s == "Neuro ICU": return "Neuro"
    return "Surgical/Trauma"

def calibration_parameters(y, p, max_iter=50):
    """Return calibration-in-the-large, calibration slope, and joint calibration intercept."""
    y=np.asarray(y,dtype=float)
    p=np.clip(np.asarray(p,dtype=float),1e-6,1-1e-6)
    x=logit(p)
    X=np.column_stack([np.ones(len(y)),x])
    beta=np.array([0.0,1.0])
    for _ in range(max_iter):
        mu=expit(X@beta)
        w=mu*(1-mu)
        g=X.T@(y-mu)
        H=-(X.T*w)@X
        step=np.linalg.pinv(H)@g
        bnew=beta-step
        if np.max(np.abs(bnew-beta)) < 1e-9:
            beta=bnew; break
        beta=bnew
    a=0.0
    for _ in range(max_iter):
        mu=expit(a+x)
        g=(y-mu).sum()
        h=-(mu*(1-mu)).sum()
        anew=a-g/h
        if abs(anew-a) < 1e-10:
            a=anew; break
        a=anew
    return float(a), float(beta[1]), float(beta[0])

def patient_bootstrap_delta_auc(y, p1, p0, n_boot=2000, seed=42):
    y=np.asarray(y,dtype=int); p1=np.asarray(p1,float); p0=np.asarray(p0,float)
    rng=np.random.default_rng(seed); n=len(y); vals=[]
    while len(vals) < n_boot:
        idx=rng.integers(0,n,n)
        yy=y[idx]
        if yy.min()==yy.max(): continue
        vals.append(roc_auc_score(yy,p1[idx])-roc_auc_score(yy,p0[idx]))
    vals=np.asarray(vals)
    point=roc_auc_score(y,p1)-roc_auc_score(y,p0)
    lo,hi=np.quantile(vals,[0.025,0.975])
    return point,float(lo),float(hi)

def ensure_dir(path):
    Path(path).mkdir(parents=True,exist_ok=True)
