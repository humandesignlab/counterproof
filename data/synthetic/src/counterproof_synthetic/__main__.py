"""Generate a synthetic paystub set: ``python -m counterproof_synthetic``.

Synthetic data only. Writes paystub documents plus a ground-truth manifest.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import cast, get_args

from .generator import MANIFEST_FILENAME, generate_set
from .schema import SetVariant


def main() -> int:
    parser = argparse.ArgumentParser(prog="counterproof_synthetic")
    parser.add_argument(
        "--out",
        type=Path,
        required=True,
        help="Output directory for the generated set.",
    )
    parser.add_argument("--count", type=int, default=10, help="Number of paystubs to generate.")
    parser.add_argument(
        "--variant",
        choices=get_args(SetVariant),
        default="mixed",
        help="clean, tampered, or mixed (alternating).",
    )
    parser.add_argument("--seed", type=int, default=0, help="RNG seed for reproducibility.")
    args = parser.parse_args()

    manifest = generate_set(
        out_dir=args.out,
        count=args.count,
        variant=cast(SetVariant, args.variant),
        seed=args.seed,
    )
    tampered = sum(1 for case in manifest.cases if case.variant == "tampered")
    print(
        f"Generated {len(manifest.cases)} paystub(s) "
        f"({tampered} tampered) in {args.out} -> {MANIFEST_FILENAME}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
