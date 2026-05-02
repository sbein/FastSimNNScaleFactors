#!/usr/bin/env bash
set -euo pipefail


MODEL_DIR=/data/dust/user/beinsam/FastSim/ScaleFactors/CMSSW_15_0_16/src/models
BASE_JSON_DIR=/data/dust/user/beinsam/FastSim/ScaleFactors/LWTNN/payloads/Run3_NanoAODv15
OUT=payload_validation_summary.txt

printf "%-75s  %-18s  %-12s  %-12s\n" "model" "object" "global_max" "global_mean" | tee "$OUT"

for pt in ${MODEL_DIR}/eff_classifier_pMSSM_334_105076_*.pt; do
  base=$(basename "$pt" .pt)

  if [[ "$base" == *GenElectron* ]]; then
    obj=Electron
    json="${BASE_JSON_DIR}/EGM/Electron/${base}.lwtnn.json"
  elif [[ "$base" == *GenLowPtElectron* ]]; then
    obj=LowPtElectron
    json="${BASE_JSON_DIR}/EGM/LowPtElectron/${base}.lwtnn.json"
  elif [[ "$base" == *GenMuon* ]]; then
    obj=Muon
    json="${BASE_JSON_DIR}/MUO/Muon/${base}.lwtnn.json"
  elif [[ "$base" == *GenPhoton* ]]; then
    obj=Photon
    json="${BASE_JSON_DIR}/EGM/Photon/${base}.lwtnn.json"
  elif [[ "$base" == *GenTau* ]]; then
    obj=Tau
    json="${BASE_JSON_DIR}/TAU/Tau/${base}.lwtnn.json"
  else
    continue
  fi

  if [[ ! -f "$json" ]]; then
    printf "%-75s  %-18s  %-12s  %-12s\n" "$base" "$obj" "MISSING" "MISSING" | tee -a "$OUT"
    continue
  fi

  echo "Validating $base"
  out=$(python3 validate_lwtnn_vs_torch.py --pt "$pt" --json "$json" -n 2000 | tail -n 2)
  gmax=$(echo "$out" | head -n1 | awk '{print $NF}')
  gmean=$(echo "$out" | tail -n1 | awk '{print $NF}')
  printf "%-75s  %-18s  %-12.4e  %-12.4e\n" "$base" "$obj" "$gmax" "$gmean" | tee -a "$OUT"
done
