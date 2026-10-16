from pathlib import Path
import pandas as pd
import numpy as np
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.common import MODEL_COLUMNS

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"outputs"
checks=[]
for name,expected_n,expected_deaths in [("MIMIC",3925,760),("eICU",403,125)]:
    d=pd.read_csv(OUT/f"{name}_modeling.csv")
    checks.append((name,"N",len(d),expected_n))
    checks.append((name,"deaths",int(d.outcome.sum()),expected_deaths))
    checks.append((name,"columns",list(d.columns)==MODEL_COLUMNS,True))
    checks.append((name,"nonpositive ratio-log inputs",
                   int((~np.isfinite(d[["log2_lactate","log2_bun","log2_lhr","log2_bhr"]])).sum().sum()),0))
failed=[x for x in checks if x[2]!=x[3]]
for x in checks: print(x)
if failed:
    raise SystemExit(f"Validation failed: {failed}")
print("All cohort validation checks passed.")
