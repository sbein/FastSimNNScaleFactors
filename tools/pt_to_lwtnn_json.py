#!/usr/bin/env python3
import argparse, json, os, re
import torch
import torch.nn as nn

'''
source /cvmfs/sft.cern.ch/lcg/views/LCG_106_cuda/x86_64-el9-gcc11-opt/setup.sh
'''

# Your exact architecture
class EffClassifier(nn.Module):
    def __init__(self, input_dim=4, hidden=32, n_classes=4):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden),
            nn.ReLU(),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
            nn.Linear(hidden, n_classes),
        )
    def forward(self, x):
        return self.net(x)

def dense_layer_to_lwtnn(linear: nn.Linear, activation: str | None):
    # PyTorch Linear weight shape: [out, in]
    W = linear.weight.detach().cpu().numpy()
    b = linear.bias.detach().cpu().numpy()

    layer = {
        "architecture": "dense",
        "weights": W.reshape(-1).tolist(),  # row-major [out,in]
        "bias": b.reshape(-1).tolist(),
    }
    if activation is not None:
        layer["activation"] = activation
    return layer

def parse_model_id(pt_path: str):
    base = os.path.basename(pt_path)
    m = re.match(
        r"eff_classifier_(.+)_(GenElectron|GenLowPtElectron|GenMuon|GenPhoton|GenTau)(?:_(.+))?\.pt$",
        base,
    )
    if not m:
        return {"process": None, "tree": None, "id": None}
    process, tree, id_name = m.groups()
    return {
        "process": process,
        "tree": tree,
        "id": id_name or "default",
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pt", help="Path to .pt (state_dict) file")
    ap.add_argument("-o", "--out", default=None, help="Output JSON path (default: <pt>.lwtnn.json)")

    ap.add_argument("--hidden", type=int, default=32)

    ap.add_argument("--inputs", nargs=4, default=["pt_log10", "eta", "phi", "iso_log10"],
                    help="Input variable names (must be 4)")
    ap.add_argument("--outputs", nargs=4, default=["p11", "p10", "p01", "p00"],
                    help="Output labels (must be 4)")

    # preprocessing metadata (NOT applied by lwtnn; for documentation + wrappers)
    ap.add_argument("--pt-eps", type=float, default=1e-4)
    ap.add_argument("--iso-eps", type=float, default=1e-6)

    args = ap.parse_args()
    out_json = args.out or (args.pt + ".lwtnn.json")

    # Load weights
    sd = torch.load(args.pt, map_location="cpu")
    model = EffClassifier(input_dim=4, hidden=args.hidden, n_classes=4)
    model.load_state_dict(sd)
    model.eval()

    # Extract linear layers
    l0: nn.Linear = model.net[0]
    l1: nn.Linear = model.net[2]
    l2: nn.Linear = model.net[4]

    ids = parse_model_id(args.pt)

    cfg = {
        "inputs": [{"name": n, "offset": 0.0, "scale": 1.0} for n in args.inputs],
        "layers": [
            dense_layer_to_lwtnn(l0, "rectified"),
            dense_layer_to_lwtnn(l1, "rectified"),
            dense_layer_to_lwtnn(l2, "softmax"),
        ],
        "outputs": list(args.outputs),
        "miscellaneous": {
            "id": ids["id"],
            "source_pt": args.pt,
            "process": ids["process"],
            "tree": ids["tree"],
            "architecture": "EffClassifier(4->hidden->hidden->4) + ReLU + softmax",
            "preprocessing": {
                "pt_log10":  {"expr": "log10(max(gen_pt, PT_EPS))",  "PT_EPS": args.pt_eps},
                "iso_log10": {"expr": "log10(max(gen_iso, ISO_EPS))", "ISO_EPS": args.iso_eps}
            },
            "prob_meaning": {
                "p11": "fast=1 full=1",
                "p10": "fast=1 full=0",
                "p01": "fast=0 full=1",
                "p00": "fast=0 full=0"
            },
            "derived": {
                "eff_fast": "p11+p10",
                "eff_full": "p11+p01",
                "sf": "eff_full/eff_fast (0 if eff_fast==0)"
            }
        },
    }

    with open(out_json, "w") as f:
        json.dump(cfg, f, indent=2, sort_keys=False)

    print(f"Wrote: {out_json}")
    print("Inputs:", args.inputs)
    print("Outputs:", args.outputs)
    print("PT_EPS:", args.pt_eps, "ISO_EPS:", args.iso_eps)
    print("Reminder: feed features already preprocessed (pt_log10, iso_log10, etc.).")

if __name__ == "__main__":
    main()
