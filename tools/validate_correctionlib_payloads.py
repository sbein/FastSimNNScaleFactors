#!/usr/bin/env python3
import argparse
import json
import math
from pathlib import Path

import correctionlib


def main():
    parser = argparse.ArgumentParser(
        description="Load exported FastSim correctionlib payloads and evaluate one test point."
    )
    parser.add_argument("--payload-dir", default="payloads/Run3_NanoAODv15_correctionlib", type=Path)
    parser.add_argument("--pt", default=15.0, type=float)
    parser.add_argument("--eta", default=0.4, type=float)
    parser.add_argument("--phi", default=2.1, type=float)
    parser.add_argument("--iso", default=1e-3, type=float)
    args = parser.parse_args()

    payloads = sorted(args.payload_dir.rglob("*.correctionlib.json"))
    if not payloads:
        raise SystemExit(f"No .correctionlib.json files found under {args.payload_dir}")

    values = []
    for payload in payloads:
        with payload.open() as fin:
            name = json.load(fin)["corrections"][0]["name"]
        cset = correctionlib.CorrectionSet.from_file(str(payload))
        sf = cset[name].evaluate(args.pt, args.eta, args.phi, args.iso)
        if not math.isfinite(sf):
            raise ValueError(f"{payload}: non-finite scale factor {sf}")
        values.append(sf)

    print(f"validated {len(payloads)} payloads with correctionlib {correctionlib.version.version}")
    print(f"test point: pt={args.pt}, eta={args.eta}, phi={args.phi}, iso={args.iso}")
    print(f"sf range: {min(values):.17g} to {max(values):.17g}")


if __name__ == "__main__":
    main()
