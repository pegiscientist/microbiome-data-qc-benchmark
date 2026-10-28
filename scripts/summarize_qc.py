"""Summarize sparsity, prevalence, and sequencing depths for demo data."""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from scripts.validate_counts import load_tables, validate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=Path("outputs"))
    args = parser.parse_args()
    counts, metadata, truth = load_tables(args.input_dir)
    problems = validate(counts, metadata, truth)
    if problems:
        raise ValueError("; ".join(problems))

    values = counts.to_numpy()
    depths = metadata["LibrarySize"].to_numpy()
    prevalence = (values > 0).mean(axis=1)
    print(f"Samples: {counts.shape[1]}; taxa: {counts.shape[0]}")
    print(f"Zero fraction: {np.mean(values == 0):.3f}")
    print(f"Median taxon prevalence: {np.median(prevalence):.3f}")
    print(f"Depth range: {depths.min():,}–{depths.max():,}; mean: {depths.mean():,.1f}")

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(depths, bins=10)
    ax.set(xlabel="Reads per sample", ylabel="Number of samples",
           title="Synthetic sample library sizes")
    fig.tight_layout()
    output = args.input_dir / "library_size_qc.png"
    fig.savefig(output, dpi=150)
    plt.close(fig)
    print(f"Figure saved: {output}")


if __name__ == "__main__":
    main()
