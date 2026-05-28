#!/usr/bin/env python3
from pathlib import Path

import correctionlib


repo = Path(__file__).resolve().parents[1]
payload = (
    repo
    / "payloads/Run3_NanoAODv15_correctionlib/EGM/Electron/eff_classifier_pMSSM_334_105076_GenElectron_loose.correctionlib.json"
)
corr = correctionlib.CorrectionSet.from_file(str(payload))[
    "fastsim_sf_pMSSM_334_105076_GenElectron_loose"
]

# For reco Electron index my_index:
# gen_index = Electron_genPartIdx[my_index]
# pt, eta, phi = GenPart_pt[gen_index], GenPart_eta[gen_index], GenPart_phi[gen_index]
# iso is the matched-particle generator isolation definition used in training.
pt, eta, phi, iso = 15.0, 0.4, 2.1, 1e-3
print(f"sf_full_over_fast {corr.evaluate(pt, eta, phi, iso):.17g}")
