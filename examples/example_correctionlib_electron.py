#!/usr/bin/env python3
from pathlib import Path

import correctionlib
import ROOT


payload = "payloads/Run3_NanoAODv15_correctionlib/EGM/Electron/eff_classifier_pMSSM_334_105076_GenElectron_loose.correctionlib.json"
correction_name = "fastsim_sf_pMSSM_334_105076_GenElectron_loose"
corr = correctionlib.CorrectionSet.from_file(str(payload))[correction_name]
tiny_nano = "examples/data/ttbar_fastsim_nano_3events.root"


def sf_from_kinematics(pt, eta, phi, iso):
    return corr.evaluate(pt, eta, phi, iso)


def sf_from_gen_index(gen_index, event):
    if gen_index < 0:
        return 1.0
    return sf_from_kinematics(event.GenPart_pt[gen_index], event.GenPart_eta[gen_index], event.GenPart_phi[gen_index], event.GenPart_iso[gen_index])


nano_file = ROOT.TFile.Open(str(tiny_nano))
events = nano_file.Get("Events")
for event_index, event in enumerate(events):
    # Analyst chooses collection, applies ID/isolation/selection cuts, then gets the SF.
    for electron_index, gen_index in enumerate(event.Electron_genPartIdx):
        sf = sf_from_gen_index(gen_index, event)
        print(f"event {event_index} electron {electron_index}: sf_full_over_fast {sf:.17g}")

sf_scan = sf_from_kinematics(pt=15.0, eta=0.4, phi=2.1, iso=1e-3)
print(f"kinematic scan point: sf_full_over_fast {sf_scan:.17g}")
