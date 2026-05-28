#!/usr/bin/env python3
import argparse
import copy
import json
from pathlib import Path


FINALIZER = "(x[0]+x[1] > 0) * (x[0]+x[2]) / max(x[0]+x[1], 1e-10)"
PT_TRANSFORM = "log10(max(x, 1e-4))"
ISO_TRANSFORM = "log10(max(x, 1e-6))"


def formula(expression, variables):
    return {
        "nodetype": "formula",
        "expression": expression,
        "parser": "TFormula",
        "variables": variables,
    }


def correction_name(path):
    name = path.name.removesuffix(".lwtnn.json")
    return name.replace("eff_classifier_", "fastsim_sf_")


def correctionlib_payload(lwtnn_payload, name):
    lwtnn = copy.deepcopy(lwtnn_payload)
    input_names = [item["name"] for item in lwtnn["inputs"]]
    expected = ["pt_log10", "eta", "phi", "iso_log10"]
    if input_names != expected:
        raise ValueError(f"{name}: expected inputs {expected}, found {input_names}")

    lwtnn["inputs"][0]["name"] = "pt"
    lwtnn["inputs"][3]["name"] = "iso"

    node = {
        "nodetype": "lwtnn",
        "opaque": lwtnn,
        "finalizer": formula(FINALIZER, ["p11", "p10", "p01", "p00"]),
    }
    for var_name, expression in [
        ("iso", ISO_TRANSFORM),
        ("pt", PT_TRANSFORM),
    ]:
        node = {
            "nodetype": "transform",
            "input": var_name,
            "rule": formula(expression, [var_name]),
            "content": node,
        }

    return {
        "schema_version": 2,
        "description": "FastSim-to-FullSim object scale factor from an LWTNN neural-network payload.",
        "corrections": [
            {
                "name": name,
                "version": 1,
                "description": (
                    "Inputs are generator-level pt, eta, phi, and isolation for the "
                    "generator particle matched to the reco object. The correction applies "
                    "log10(max(pt, 1e-4)) and log10(max(iso, 1e-6)) internally."
                ),
                "inputs": [
                    {"name": "pt", "type": "real", "description": "matched generator-particle pt"},
                    {"name": "eta", "type": "real", "description": "matched generator-particle eta"},
                    {"name": "phi", "type": "real", "description": "matched generator-particle phi"},
                    {
                        "name": "iso",
                        "type": "real",
                        "description": "matched generator-particle isolation, defined as in training",
                    },
                ],
                "output": {
                    "name": "sf_full_over_fast",
                    "type": "real",
                    "description": "(p11 + p01) / (p11 + p10)",
                },
                "data": node,
            }
        ],
    }


def output_path(input_path, input_dir, output_dir):
    rel = input_path.relative_to(input_dir)
    return (output_dir / rel).with_name(rel.name.removesuffix(".lwtnn.json") + ".correctionlib.json")


def main():
    parser = argparse.ArgumentParser(
        description="Wrap FastSim LWTNN JSON payloads as correctionlib CorrectionSet JSON files."
    )
    parser.add_argument("--input-dir", default="payloads/Run3_NanoAODv15", type=Path)
    parser.add_argument("--output-dir", default="payloads/Run3_NanoAODv15_correctionlib", type=Path)
    parser.add_argument("--indent", default=2, type=int)
    args = parser.parse_args()

    inputs = sorted(args.input_dir.rglob("*.lwtnn.json"))
    if not inputs:
        raise SystemExit(f"No .lwtnn.json files found under {args.input_dir}")

    for input_file in inputs:
        with input_file.open() as fin:
            lwtnn_payload = json.load(fin)
        payload = correctionlib_payload(lwtnn_payload, correction_name(input_file))
        target = output_path(input_file, args.input_dir, args.output_dir)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w") as fout:
            json.dump(payload, fout, indent=args.indent)
            fout.write("\n")

    print(f"Wrote {len(inputs)} correctionlib payloads to {args.output_dir}")


if __name__ == "__main__":
    main()
