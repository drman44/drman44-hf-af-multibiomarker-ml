"""
Reference implementation of the locked internal-validation design.

The canonical numerical internal-validation results are preserved in reference_outputs/.
The central external validation is exactly reproducible in 04_external_validation.py.

Important: surviving run artifacts preserve every selected fold-level tree hyperparameter and the
exact XGBoost/LightGBM candidates that won across folds, but do not preserve every losing
Random-Forest/Decision-Tree candidate from the historical inner-search grid. Accordingly this file
documents the leakage-protected nesting pattern and can be used to re-run the regularized linear
models and preserved tree configurations; it does not invent unrecovered discarded candidates.
"""
from pathlib import Path
import json, sys
import numpy as np
import pandas as pd
from sklearn.model_selection import RepeatedStratifiedKFold, StratifiedKFold
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, log_loss, brier_score_loss

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.common import CATEGORICAL

ROOT=Path(__file__).resolve().parents[1]
df=pd.read_csv(ROOT/"outputs"/"MIMIC_modeling.csv")
X=df.drop(columns="outcome"); y=df.outcome.to_numpy()
num=[c for c in X.columns if c not in CATEGORICAL]

# Phase-1 retained execution record.
outer=RepeatedStratifiedKFold(n_splits=5,n_repeats=3,random_state=20260804)
C_GRID=[0.1,0.3]
L1_GRID=[0.25,0.75]

def prep():
    return ColumnTransformer([
        ("num",Pipeline([("imp",SimpleImputer(strategy="median")),("scale",StandardScaler())]),num),
        ("cat",Pipeline([("imp",SimpleImputer(strategy="most_frequent")),
                         ("ohe",OneHotEncoder(handle_unknown="ignore",sparse_output=False))]),CATEGORICAL)
    ],verbose_feature_names_out=False)

def run_linear(kind):
    preds=np.full((3,len(df)),np.nan)
    rows=[]
    for oi,(tr,va) in enumerate(outer.split(X,y)):
        rep=oi//5; fold=oi%5
        inner=StratifiedKFold(n_splits=3,shuffle=True,random_state=20260804+oi)
        candidates=[]
        for C in C_GRID:
            ratios=[1.0] if kind=="lasso" else L1_GRID
            for l1 in ratios:
                losses=[]
                for a,b in inner.split(X.iloc[tr],y[tr]):
                    p=prep()
                    Xt=p.fit_transform(X.iloc[tr].iloc[a])
                    Xv=p.transform(X.iloc[tr].iloc[b])
                    model=LogisticRegression(
                        solver="saga",C=C,l1_ratio=l1,max_iter=5000,random_state=20260804+oi
                    )
                    model.fit(Xt,y[tr][a])
                    losses.append(log_loss(y[tr][b],model.predict_proba(Xv)[:,1]))
                candidates.append((np.mean(losses),C,l1))
        _,C,l1=min(candidates,key=lambda x:x[0])
        p=prep()
        Xt=p.fit_transform(X.iloc[tr]); Xv=p.transform(X.iloc[va])
        model=LogisticRegression(solver="saga",C=C,l1_ratio=l1,max_iter=5000,random_state=20260804+oi)
        model.fit(Xt,y[tr])
        pr=model.predict_proba(Xv)[:,1]
        preds[rep,va]=pr
        rows.append([rep+1,fold+1,C,l1])
    flat_y=np.tile(y,3); flat_p=preds.reshape(-1)
    print(kind, "pooled OOF AUC", roc_auc_score(flat_y,flat_p),
          "Brier",brier_score_loss(flat_y,flat_p),"logloss",log_loss(flat_y,flat_p))
    return pd.DataFrame(rows,columns=["repeat","fold","C","l1_ratio"])

if __name__=="__main__":
    run_linear("lasso").to_csv(ROOT/"outputs"/"lasso_rerun_settings.csv",index=False)
    run_linear("elastic_net").to_csv(ROOT/"outputs"/"elastic_net_rerun_settings.csv",index=False)
