#!/usr/bin/env python3
import math
import subprocess

PT_EPS  = 1e-4
ISO_EPS = 1e-6

def safe_log10(x, eps):
    return math.log10(max(float(x), float(eps)))

def lwtnn_probs(eval_exe, json_path, pt_log10, eta, phi, iso_log10):
    """
    Calls your compiled eval_lwtnn and parses p11,p10,p01,p00.
    """
    r = subprocess.check_output(
        [eval_exe, json_path, str(pt_log10), str(eta), str(phi), str(iso_log10)],
        text=True
    )
    vals = {}
    for line in r.strip().splitlines():
        k, v = line.split()
        vals[k] = float(v)
    return vals

def fastsim_effs_sf_from_probs(p):
    p11 = p["p11"]; p10 = p["p10"]; p01 = p["p01"]
    eff_fast = p11 + p10
    eff_full = p11 + p01
    sf = (eff_full / eff_fast) if eff_fast > 0 else 0.0
    return eff_fast, eff_full, sf

def main():
    json_path = (
        "/data/dust/user/beinsam/FastSim/ScaleFactors/LWTNN/lwtnn_json/"
        "eff_classifier_pMSSM_334_105076_GenElectron.lwtnn.json"
    )
    eval_exe = "./eval_lwtnn"

    # ------------------------------------------------------------
    # PSEUDOCODE (commented) for NanoAOD via uproot:
    # import uproot
    # f = uproot.open("NANO.root")
    # t = f["Events"]
    # ele_pt = t["Electron_pt"].array(library="np")
    # ele_genidx = t["Electron_genPartIdx"].array(library="np")
    # gen_pt  = t["GenPart_pt"].array(library="np")
    # gen_eta = t["GenPart_eta"].array(library="np")
    # gen_phi = t["GenPart_phi"].array(library="np")
    # ------------------------------------------------------------

    # Mock values for example:
    gen_pt, gen_eta, gen_phi, gen_iso = 15.0, 0.4, 2.1, 1e-3

    pt_log10  = safe_log10(gen_pt,  PT_EPS)
    iso_log10 = safe_log10(gen_iso, ISO_EPS)

    p = lwtnn_probs(eval_exe, json_path, pt_log10, gen_eta, gen_phi, iso_log10)
    eff_fast, eff_full, sf = fastsim_effs_sf_from_probs(p)

    print("p =", p)
    print("eff_fast =", eff_fast)
    print("eff_full =", eff_full)
    print("sf =", sf)

if __name__ == "__main__":
    main()
