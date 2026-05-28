# FastSim NN correctionlib payloads for Run3 NanoAODv15

These files wrap the corresponding LWTNN neural-network payloads as correctionlib
`CorrectionSet` JSON files.

Each correction takes the matched generator-particle quantities:

```text
pt
eta
phi
iso
```

The correction handles the internal preprocessing:

```text
pt_log10 = log10(max(pt, 1e-4))
iso_log10 = log10(max(iso, 1e-6))
```

The output is:

```text
sf_full_over_fast = (p11 + p01) / (p11 + p10)
```

The correction names are derived from the payload names, for example:

```text
fastsim_sf_pMSSM_334_105076_GenElectron_loose
```

The payloads in this directory are generated from the standalone LWTNN payloads
with:

```bash
python3 tools/export_correctionlib_payloads.py
```
