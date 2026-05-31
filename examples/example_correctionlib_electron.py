#!/usr/bin/env python3
from pathlib import Path
from types import SimpleNamespace

import correctionlib


repo = Path(__file__).resolve().parents[1]
payload = (
    repo
    / "payloads/Run3_NanoAODv15_correctionlib/EGM/Electron/eff_classifier_pMSSM_334_105076_GenElectron_loose.correctionlib.json"
)
corr = correctionlib.CorrectionSet.from_file(str(payload))[
    "fastsim_sf_pMSSM_334_105076_GenElectron_loose"
]
tiny_nano = repo / "examples/data/ttbar_fastsim_nano_3events.root"


def fastsim2fullsim_sf_from_kinematics(pt, eta, phi, iso):
    return corr.evaluate(pt, eta, phi, iso)


def bind_fastsim2fullsim_sf_to_event(event):
    def fastsim2fullsim_sf_from_gen_index(gen_index):
        if gen_index < 0:
            return 1.0
        return fastsim2fullsim_sf_from_kinematics(
            event.GenPart_pt[gen_index],
            event.GenPart_eta[gen_index],
            event.GenPart_phi[gen_index],
            event.GenPart_iso[gen_index],
        )

    return fastsim2fullsim_sf_from_gen_index


def tiny_nano_events():
    try:
        import ROOT
    except ImportError:
        yield SimpleNamespace(
            Electron_genPartIdx=[2],
            GenPart_pt=[5.0, 12.0, 15.0],
            GenPart_eta=[-1.1, 1.3, 0.4],
            GenPart_phi=[0.2, -2.4, 2.1],
            GenPart_iso=[0.02, 0.01, 1e-3],
        )
        return

    nano_file = ROOT.TFile.Open(str(tiny_nano))
    events = nano_file.Get("Events")
    for event in events:
        yield event


for event_index, event in enumerate(tiny_nano_events()):
    sf_from_gen_index = bind_fastsim2fullsim_sf_to_event(event)
    # Analyst chooses collection, applies ID/isolation/selection cuts, then gets the SF.
    for electron_index, gen_index in enumerate(event.Electron_genPartIdx):
        sf = sf_from_gen_index(gen_index)
        print(f"event {event_index} electron {electron_index}: sf_full_over_fast {sf:.17g}")

sf_scan = fastsim2fullsim_sf_from_kinematics(pt=15.0, eta=0.4, phi=2.1, iso=1e-3)
print(f"kinematic scan point: sf_full_over_fast {sf_scan:.17g}")
