from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
IN=ROOT/"data"/"restricted"
OUT=ROOT/"outputs"

def _smd_cont(a,b):
    a=pd.to_numeric(a,errors="coerce").dropna()
    b=pd.to_numeric(b,errors="coerce").dropna()
    s=np.sqrt((a.var(ddof=1)+b.var(ddof=1))/2)
    return 0.0 if not np.isfinite(s) or s==0 else (a.mean()-b.mean())/s

def _smd_bin(a,b):
    a=pd.Series(a).dropna().astype(float); b=pd.Series(b).dropna().astype(float)
    p1=a.mean(); p0=b.mean()
    d=np.sqrt((p1*(1-p1)+p0*(1-p0))/2)
    return 0.0 if not np.isfinite(d) or d==0 else (p1-p0)/d

def _mediqr(s):
    s=pd.to_numeric(s,errors="coerce").dropna()
    return f"{s.median():.1f} [{s.quantile(.25):.1f}-{s.quantile(.75):.1f}]"

def _npct(s):
    s=pd.Series(s).dropna().astype(float)
    return f"{int(s.sum())} ({100*s.mean():.1f}%)"

def prep_mimic(df):
    x=pd.DataFrame(index=df.index)
    x["included"]=df["lactate"].notna()&(df["lactate"]>0)
    x["outcome"]=df["inhospital_mortality_after_landmark"].astype(int)
    x["age"]=df["age"]; x["female"]=(df["gender"]=="F").astype(int); x["weight"]=df["weight"]
    x["sbp"]=df["systolic_blood_pressure"]; x["dbp"]=df["diastolic_blood_pressure"]
    x["heart_rate"]=df["heart_rate"]; x["resp_rate"]=df["respiratory_rate"]
    x["bun"]=df["bun_mg_dl"]; x["hemoglobin"]=df["hemoglobin_g_dl"]; x["bhr"]=df["bhr"]
    for src,dst in [("platelet_count","platelet"),("wbc","wbc"),("rdw","rdw"),("glucose","glucose"),
                    ("creatinine","creatinine"),("calcium","calcium"),("potassium","potassium"),("anion_gap","anion_gap")]:
        x[dst]=df[src]
    for src,dst in [("myocardial_infarction","mi"),("cerebrovascular_disease","cvd"),
                    ("chronic_pulmonary_disease","copd"),("diabetes","diabetes"),
                    ("chronic_renal_disease","ckd"),("malignancy","malignancy"),
                    ("severe_liver_disease","severe_liver"),("hypertension","hypertension"),("anemia","anemia")]:
        x[dst]=df[src].astype(int)
    return x

def prep_eicu(df):
    x=pd.DataFrame(index=df.index)
    x["included"]=df["lactate"].notna()&(df["lactate"]>0)
    x["outcome"]=df["inhospital_mortality_after_landmark"].astype(int)
    x["age"]=pd.to_numeric(df["age"],errors="coerce"); x["female"]=(df["sex"]=="Female").astype(int)
    x["weight"]=df["admission_weight_kg"]; x["sbp"]=df["systolic_blood_pressure"]; x["dbp"]=df["diastolic_blood_pressure"]
    x["heart_rate"]=df["heart_rate"]; x["resp_rate"]=df["respiratory_rate"]
    x["bun"]=df["bun_mg_dl"]; x["hemoglobin"]=df["hemoglobin_g_dl"]; x["bhr"]=df["bhr"]
    for src,dst in [("platelet_count","platelet"),("wbc","wbc"),("rdw","rdw"),("glucose","glucose"),
                    ("creatinine","creatinine"),("calcium","calcium"),("potassium","potassium"),("anion_gap","anion_gap")]:
        x[dst]=df[src]
    for src,dst in [("myocardial_infarction","mi"),("cerebrovascular_disease","cvd"),
                    ("chronic_pulmonary_disease","copd"),("diabetes","diabetes"),
                    ("chronic_renal_disease","ckd"),("malignancy","malignancy"),
                    ("severe_liver_disease","severe_liver"),("hypertension","hypertension"),("anemia","anemia")]:
        x[dst]=df[src].astype(int)
    return x

if __name__=="__main__":
    m=prep_mimic(pd.read_csv(IN/"BHR_MIMIC_analysis_ready.csv"))
    e=prep_eicu(pd.read_csv(IN/"BHR_eICU_analysis_ready.csv"))
    overview=[]
    detail=[]
    continuous=["age","weight","sbp","dbp","heart_rate","resp_rate","bun","hemoglobin","bhr",
                "platelet","wbc","rdw","glucose","creatinine","calcium","potassium","anion_gap"]
    binary=["outcome","female","mi","cvd","copd","diabetes","ckd","malignancy","severe_liver","hypertension","anemia"]
    for cohort,d in [("MIMIC-IV",m),("eICU",e)]:
        inc=d[d.included]; exc=d[~d.included]
        overview.append([cohort,len(d),len(inc),len(exc),100*len(inc)/len(d),
                         int(inc.outcome.sum()),100*inc.outcome.mean(),
                         int(exc.outcome.sum()),100*exc.outcome.mean()])
        for v in continuous:
            detail.append([cohort,v,"Continuous",_mediqr(inc[v]),_mediqr(exc[v]),_smd_cont(inc[v],exc[v])])
        for v in binary:
            detail.append([cohort,v,"Binary",_npct(inc[v]),_npct(exc[v]),_smd_bin(inc[v],exc[v])])
    pd.DataFrame(overview,columns=[
        "cohort","landmark_N","included_N","excluded_N","included_pct",
        "included_deaths","included_mortality_pct","excluded_deaths","excluded_mortality_pct"
    ]).to_csv(OUT/"reviewer_completeness_overview.csv",index=False)
    pd.DataFrame(detail,columns=[
        "cohort","characteristic","type","included_complete_biomarker",
        "excluded_incomplete_biomarker","SMD_included_minus_excluded"
    ]).to_csv(OUT/"reviewer_completeness_characteristics.csv",index=False)
    print("Biomarker-completeness selection outputs written.")
