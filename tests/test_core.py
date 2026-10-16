import sys
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.common import collapse_mimic_race, collapse_eicu_race, collapse_mimic_unit, collapse_eicu_unit, calibration_parameters

def test_race_harmonization():
    assert collapse_mimic_race("WHITE - RUSSIAN")=="White"
    assert collapse_mimic_race("PORTUGUESE")=="White"
    assert collapse_mimic_race("BLACK/AFRICAN AMERICAN")=="Black"
    assert collapse_eicu_race("Caucasian")=="White"
    assert collapse_eicu_race("African American")=="Black"

def test_unit_harmonization():
    assert collapse_mimic_unit("Cardiac Vascular Intensive Care Unit (CVICU)")=="Cardiac"
    assert collapse_mimic_unit("Neuro Surgical Intensive Care Unit (Neuro SICU)")=="Surgical/Trauma"
    assert collapse_eicu_unit("MICU")=="Medical"

def test_calibration_perfect_probabilities():
    rng=np.random.default_rng(1)
    p=np.linspace(.05,.8,2000)
    y=rng.binomial(1,p)
    citl,slope,joint=calibration_parameters(y,p)
    assert np.isfinite(citl) and np.isfinite(slope) and np.isfinite(joint)
    assert 0.5 < slope < 1.5
