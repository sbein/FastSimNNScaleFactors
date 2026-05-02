#!/usr/bin/env python3
import argparse, subprocess, numpy as np, torch, torch.nn as nn

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

def torch_eval(pt_path, X):
    sd = torch.load(pt_path, map_location="cpu")
    m = EffClassifier()
    m.load_state_dict(sd)
    m.eval()
    with torch.no_grad():
        logits = m(torch.from_numpy(X.astype(np.float32)))
        probs = torch.softmax(logits, dim=1).numpy()
    return probs

def lwtnn_eval(exe, json_path, X):
    # call C++ exe point-by-point (fine for ~1e4; can batch later)
    out = np.zeros((X.shape[0], 4), dtype=np.float64)
    for i, (a,b,c,d) in enumerate(X):
        r = subprocess.check_output([exe, json_path, str(a), str(b), str(c), str(d)], text=True)
        # parse lines "p11 val"
        vals = {}
        for line in r.strip().splitlines():
            k, v = line.split()
            vals[k] = float(v)
        out[i,0] = vals["p11"]
        out[i,1] = vals["p10"]
        out[i,2] = vals["p01"]
        out[i,3] = vals["p00"]
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pt", required=True)
    ap.add_argument("--json", required=True)
    ap.add_argument("--exe", default="./eval_lwtnn")
    ap.add_argument("-n", type=int, default=2000)
    args = ap.parse_args()

    # generate reasonable-ish random feature space
    rng = np.random.default_rng(123)
    # pt_log10 in [0, 3], eta in [-2.5,2.5], phi in [-pi,pi], iso_log10 in [-6, 1]
    X = np.column_stack([
        rng.uniform(0.0, 3.0, args.n),
        rng.uniform(-2.5, 2.5, args.n),
        rng.uniform(-np.pi, np.pi, args.n),
        rng.uniform(-6.0, 1.0, args.n),
    ]).astype(np.float32)

    t = torch_eval(args.pt, X).astype(np.float64)
    l = lwtnn_eval(args.exe, args.json, X)

    d = np.abs(t - l)
    print("Per-output max |Δ|:", d.max(axis=0))
    print("Per-output mean|Δ|:", d.mean(axis=0))
    print("Global max |Δ|:", d.max())
    print("Global mean|Δ|:", d.mean())

if __name__ == "__main__":
    main()
