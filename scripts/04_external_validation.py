from pathlib import Path
import json, sys
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, brier_score_loss, log_loss
from xgboost import XGBClassifier

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.common import CATEGORICAL, MODEL_FEATURES

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"outputs"
m=pd.read_csv(OUT/"MIMIC_modeling.csv")
e=pd.read_csv(OUT/"eICU_modeling.csv")
y=e.outcome.to_numpy()

def logistic_pipeline(features):
    cats=[c for c in CATEGORICAL if c in features]
    nums=[c for c in features if c not in cats]
    pre=ColumnTransformer([
        ("num",Pipeline([("imp",SimpleImputer(strategy="median")),("scale",StandardScaler())]),nums),
        ("cat",Pipeline([("imp",SimpleImputer(strategy="most_frequent")),
                         ("ohe",OneHotEncoder(handle_unknown="ignore",sparse_output=False))]),cats)
    ],verbose_feature_names_out=False)
    # Historical comparators were effectively unpenalized; C=1e6 reproduces the retained predictions.
    model=LogisticRegression(solver="lbfgs",C=1e6,max_iter=4000)
    return Pipeline([("prep",pre),("model",model)])

def xgb_pipeline(features):
    cats=[c for c in CATEGORICAL if c in features]
    nums=[c for c in features if c not in cats]
    pre=ColumnTransformer([
        ("num",SimpleImputer(strategy="median"),nums),
        ("cat",Pipeline([("imp",SimpleImputer(strategy="most_frequent")),
                         ("ohe",OneHotEncoder(handle_unknown="ignore",sparse_output=False))]),cats)
    ],verbose_feature_names_out=False)
    model=XGBClassifier(
        n_estimators=180,max_depth=3,learning_rate=0.035,subsample=0.9,
        colsample_bytree=0.9,reg_lambda=3.0,random_state=42,n_jobs=1,
        eval_metric="logloss",tree_method="hist"
    )
    return Pipeline([("prep",pre),("model",model)])

pred=pd.DataFrame({"outcome":y})
metrics=[]
for name,features in MODEL_FEATURES.items():
    pipe=logistic_pipeline(features)
    pipe.fit(m[features],m.outcome)
    p=pipe.predict_proba(e[features])[:,1]
    pred[name]=p
    metrics.append([name,roc_auc_score(y,p),brier_score_loss(y,p),log_loss(y,p)])

all_features=[c for c in m.columns if c!="outcome"]
pipe=xgb_pipeline(all_features)
pipe.fit(m[all_features],m.outcome)
p=pipe.predict_proba(e[all_features])[:,1]
pred["Locked XGBoost"]=p
metrics.append(["Locked XGBoost",roc_auc_score(y,p),brier_score_loss(y,p),log_loss(y,p)])

pd.DataFrame(metrics,columns=["model","AUC","Brier","LogLoss"]).to_csv(OUT/"external_model_performance_rerun.csv",index=False)
pred.to_csv(OUT/"eICU_external_predictions_LOCAL_RESTRICTED.csv",index=False)

# Exact-value gates from the retained locked run.
gate=pd.DataFrame(metrics,columns=["model","AUC","Brier","LogLoss"]).set_index("model")
assert abs(gate.loc["Locked XGBoost","AUC"]-0.6676258992805756) < 1e-10
assert abs(gate.loc["Locked XGBoost","Brier"]-0.20359885692596436) < 1e-10
assert abs(gate.loc["Clinical + raw components","AUC"]-0.6716258992805756) < 1e-10
print(gate.round(6))
print("Locked external validation reproduced.")
