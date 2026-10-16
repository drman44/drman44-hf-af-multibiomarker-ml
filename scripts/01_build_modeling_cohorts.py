from pathlib import Path
import numpy as np
import pandas as pd
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.common import MODEL_COLUMNS, collapse_mimic_race, collapse_eicu_race, collapse_mimic_unit, collapse_eicu_unit, ensure_dir

ROOT=Path(__file__).resolve().parents[1]
IN=ROOT/"data"/"restricted"
OUT=ROOT/"outputs"
ensure_dir(OUT)

MIMIC_REQUIRED = {
"inhospital_mortality_after_landmark","age","gender","race","weight","systolic_blood_pressure",
"diastolic_blood_pressure","heart_rate","respiratory_rate","platelet_count","wbc","rbc","rdw",
"glucose","creatinine","calcium","potassium","anion_gap","lactate","bun_mg_dl","hemoglobin_g_dl",
"myocardial_infarction","peripheral_vascular_disease","cerebrovascular_disease","chronic_pulmonary_disease",
"rheumatic_disease","peptic_ulcer_disease","diabetes","chronic_renal_disease","malignancy",
"severe_liver_disease","hypertension","anemia","first_careunit"
}
EICU_REQUIRED = {
"inhospital_mortality_after_landmark","age","sex","race_ethnicity","admission_weight_kg",
"systolic_blood_pressure","diastolic_blood_pressure","heart_rate","respiratory_rate","platelet_count","wbc",
"rbc","rdw","glucose","creatinine","calcium","potassium","anion_gap","lactate","bun_mg_dl","hemoglobin_g_dl",
"myocardial_infarction","peripheral_vascular_disease","cerebrovascular_disease","chronic_pulmonary_disease",
"rheumatic_disease","peptic_ulcer_disease","diabetes","chronic_renal_disease","malignancy",
"severe_liver_disease","hypertension","anemia","unit_type"
}

COMORBID=[
("myocardial_infarction","mi"),("peripheral_vascular_disease","pvd"),
("cerebrovascular_disease","cvd"),("chronic_pulmonary_disease","copd"),
("rheumatic_disease","rheumatic"),("peptic_ulcer_disease","pud"),
("diabetes","diabetes"),("chronic_renal_disease","ckd"),("malignancy","malignancy"),
("severe_liver_disease","severe_liver"),("hypertension","hypertension"),("anemia","anemia")
]

def _check(df, required, label):
    missing=sorted(required-set(df.columns))
    if missing:
        raise ValueError(f"{label} missing columns: {missing}")

def build_mimic(df):
    _check(df,MIMIC_REQUIRED,"MIMIC")
    d=df.loc[df.lactate.notna()&(df.lactate>0)&(df.bun_mg_dl>0)&(df.hemoglobin_g_dl>0)].copy()
    o=pd.DataFrame(index=d.index)
    o["outcome"]=d.inhospital_mortality_after_landmark.astype(int)
    o["age"]=d.age
    o["sex"]=d.gender.map({"F":"Female","M":"Male"})
    o["race"]=d.race.map(collapse_mimic_race)
    o["unit_type"]=d.first_careunit.map(collapse_mimic_unit)
    o["weight"]=d.weight; o["sbp"]=d.systolic_blood_pressure; o["dbp"]=d.diastolic_blood_pressure
    o["heart_rate"]=d.heart_rate; o["resp_rate"]=d.respiratory_rate
    o["platelet"]=d.platelet_count; o["wbc"]=d.wbc; o["rbc"]=d.rbc; o["rdw"]=d.rdw
    o["glucose"]=d.glucose; o["creatinine"]=d.creatinine; o["calcium"]=d.calcium
    o["potassium"]=d.potassium; o["anion_gap"]=d.anion_gap
    o["hemoglobin"]=d.hemoglobin_g_dl
    o["log2_lactate"]=np.log2(d.lactate); o["log2_bun"]=np.log2(d.bun_mg_dl)
    o["log2_lhr"]=np.log2(d.lactate/d.hemoglobin_g_dl)
    o["log2_bhr"]=np.log2(d.bun_mg_dl/d.hemoglobin_g_dl)
    for src,dst in COMORBID: o[dst]=d[src].astype(int)
    return o[MODEL_COLUMNS].reset_index(drop=True)

def build_eicu(df):
    _check(df,EICU_REQUIRED,"eICU")
    d=df.loc[df.lactate.notna()&(df.lactate>0)&(df.bun_mg_dl>0)&(df.hemoglobin_g_dl>0)].copy()
    o=pd.DataFrame(index=d.index)
    o["outcome"]=d.inhospital_mortality_after_landmark.astype(int)
    o["age"]=pd.to_numeric(d.age,errors="coerce")
    o["sex"]=d.sex
    o["race"]=d.race_ethnicity.map(collapse_eicu_race)
    o["unit_type"]=d.unit_type.map(collapse_eicu_unit)
    o["weight"]=d.admission_weight_kg; o["sbp"]=d.systolic_blood_pressure; o["dbp"]=d.diastolic_blood_pressure
    o["heart_rate"]=d.heart_rate; o["resp_rate"]=d.respiratory_rate
    o["platelet"]=d.platelet_count; o["wbc"]=d.wbc; o["rbc"]=d.rbc; o["rdw"]=d.rdw
    o["glucose"]=d.glucose; o["creatinine"]=d.creatinine; o["calcium"]=d.calcium
    o["potassium"]=d.potassium; o["anion_gap"]=d.anion_gap
    o["hemoglobin"]=d.hemoglobin_g_dl
    o["log2_lactate"]=np.log2(d.lactate); o["log2_bun"]=np.log2(d.bun_mg_dl)
    o["log2_lhr"]=np.log2(d.lactate/d.hemoglobin_g_dl)
    o["log2_bhr"]=np.log2(d.bun_mg_dl/d.hemoglobin_g_dl)
    for src,dst in COMORBID: o[dst]=d[src].astype(int)
    return o[MODEL_COLUMNS].reset_index(drop=True)

if __name__=="__main__":
    m0=pd.read_csv(IN/"BHR_MIMIC_analysis_ready.csv")
    e0=pd.read_csv(IN/"BHR_eICU_analysis_ready.csv")
    m=build_mimic(m0); e=build_eicu(e0)
    m.to_csv(OUT/"MIMIC_modeling.csv",index=False)
    e.to_csv(OUT/"eICU_modeling.csv",index=False)
    print(f"MIMIC modeling cohort: N={len(m)}, deaths={int(m.outcome.sum())}")
    print(f"eICU modeling cohort: N={len(e)}, deaths={int(e.outcome.sum())}")
