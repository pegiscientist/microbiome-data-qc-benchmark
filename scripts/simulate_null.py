"""Create a small synthetic microbiome null dataset.

The case/control labels do not affect the data-generating process.
This is an educational QC example, not a biologically calibrated simulator.
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def simulate(seed=42, n_samples=40, n_taxa=60, mean_depth=10000):
    if n_samples < 2 or n_samples % 2 or n_taxa < 2 or mean_depth <= 0:
        raise ValueError("Use an even sample count >=2, >=2 taxa, and positive mean depth.")

    rng = np.random.default_rng(seed)
    sample_ids = [f"Sample_{i:03d}" for i in range(1, n_samples + 1)]
    taxon_ids = [f"Taxon_{j:03d}" for j in range(1, n_taxa + 1)]
    groups = np.array(["Control"] * (n_samples // 2) + ["Case"] * (n_samples // 2))
    # Shuffle the labels; the count generation below does not depend on group.
    rng.shuffle(groups)

    # Shared baseline, with modest sample-to-sample compositional variability.
    baseline = rng.dirichlet(np.full(n_taxa, 0.5))
    depths = rng.poisson(mean_depth, size=n_samples).clip(min=1)
    composition = np.vstack([rng.dirichlet(100 * baseline + 0.05) for _ in sample_ids])
    counts = np.vstack([
        rng.multinomial(int(depth), p)
        for depth, p in zip(depths, composition)
    ]).T

    count_df = pd.DataFrame(counts, index=taxon_ids, columns=sample_ids)
    count_df.index.name = "Taxon"
    metadata = pd.DataFrame({
        "SampleID": sample_ids, "Group": groups, "LibrarySize": depths
    })
    truth = pd.DataFrame({
        "Taxon": taxon_ids, "True_DA": np.zeros(n_taxa, dtype=int)
    })
    return count_df, metadata, truth


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    counts, metadata, truth = simulate(seed=args.seed)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    counts.to_csv(args.output_dir / "null_counts.csv")
    metadata.to_csv(args.output_dir / "null_metadata.csv", index=False)
    truth.to_csv(args.output_dir / "null_ground_truth.csv", index=False)
    print(f"Saved {counts.shape[0]} taxa x {counts.shape[1]} samples to {args.output_dir}")


if __name__ == "__main__":
    main()
