# FastSim NN scale-factor payloads for Run3 NanoAODv15

These payloads are LWTNN JSON neural-network models trained to provide FastSim-to-FullSim efficiency scale factors.

Correctionlib-wrapped versions of these payloads are available in:

```text
payloads/Run3_NanoAODv15_correctionlib/
```

Each model takes:

- `pt_log10 = log10(max(gen_pt, 1e-4))`
- `eta = gen_eta`
- `phi = gen_phi`
- `iso_log10 = log10(max(gen_iso, 1e-6))`

and outputs:

- `p11`: FastSim matched, FullSim matched
- `p10`: FastSim matched, FullSim unmatched
- `p01`: FastSim unmatched, FullSim matched
- `p00`: FastSim unmatched, FullSim unmatched

Derived quantities:

```text
eff_fast = p11 + p10
eff_full = p11 + p01
sf_full_over_fast = eff_full / eff_fast
```

The payloads have been validated by comparing direct PyTorch evaluation with LWTNN C++ evaluation. See payload_validation_summary.txt.

Current status: prototype payload set.
