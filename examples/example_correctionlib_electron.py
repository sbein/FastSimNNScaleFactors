#!/usr/bin/env python3
import json
from pathlib import Path

import correctionlib


def formula(expression, variables):
    return {
        "nodetype": "formula",
        "expression": expression,
        "parser": "TFormula",
        "variables": variables,
    }


repo = Path(__file__).resolve().parents[1]
lwtnn = json.loads(
    (
        repo
        / "payloads/Run3_NanoAODv15/EGM/Electron/eff_classifier_pMSSM_334_105076_GenElectron_loose.lwtnn.json"
    ).read_text()
)
lwtnn["inputs"][0]["name"] = "pt"
lwtnn["inputs"][3]["name"] = "iso"

node = {
    "nodetype": "lwtnn",
    "opaque": lwtnn,
    "finalizer": formula(
        "(x[0]+x[1] > 0) * (x[0]+x[2]) / max(x[0]+x[1], 1e-10)",
        ["p11", "p10", "p01", "p00"],
    ),
}
for name, expression in [
    ("iso", "log10(max(x, 1e-6))"),
    ("pt", "log10(max(x, 1e-4))"),
]:
    node = {
        "nodetype": "transform",
        "input": name,
        "rule": formula(expression, [name]),
        "content": node,
    }

cset = correctionlib.CorrectionSet.from_string(
    json.dumps(
        {
            "schema_version": 2,
            "corrections": [
                {
                    "name": "electron_loose_fastsim_sf",
                    "version": 1,
                    "inputs": [
                        {"name": "pt", "type": "real"},
                        {"name": "eta", "type": "real"},
                        {"name": "phi", "type": "real"},
                        {"name": "iso", "type": "real"},
                    ],
                    "output": {"name": "sf_full_over_fast", "type": "real"},
                    "data": node,
                }
            ],
        }
    )
)

# For reco Electron index my_index:
# gen_index = Electron_genPartIdx[my_index]
# pt, eta, phi = GenPart_pt[gen_index], GenPart_eta[gen_index], GenPart_phi[gen_index]
# iso is the matched-particle generator isolation defined consistently with training.
pt, eta, phi, iso = 15.0, 0.4, 2.1, 1e-3
sf = cset["electron_loose_fastsim_sf"].evaluate(pt, eta, phi, iso)
print(f"sf_full_over_fast {sf:.17g}")
