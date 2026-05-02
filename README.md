# FastSim NN Scale Factors

Prototype LWTNN JSON payloads for FastSim-to-FullSim object efficiency scale factors.

Payloads are under:

```text
payloads/Run3_NanoAODv15/

The models use four preprocessed generator-level inputs:

pt_log10  = log10(max(gen_pt, 1e-4))
eta       = gen_eta
phi       = gen_phi
iso_log10 = log10(max(gen_iso, 1e-6))

Outputs are:

p11 = fast_matched=1, full_matched=1
p10 = fast_matched=1, full_matched=0
p01 = fast_matched=0, full_matched=1
p00 = fast_matched=0, full_matched=0

Derived quantities:

eff_fast = p11 + p10
eff_full = p11 + p01
sf_full_over_fast = eff_full / eff_fast

Validation summary:

payloads/Run3_NanoAODv15/payload_validation_summary.txt

Status: prototype payload set.
