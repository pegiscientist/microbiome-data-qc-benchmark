"""Validate basic integrity of a synthetic microbiome count table."""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def validate(counts, metadata, truth=None):
    problems = []
    if counts.empty or metadata.empty:
        problems.append("Counts and metadata must not be empty.")
    if not counts.index.is_unique or not counts.columns.is_unique:
        problems.append("Count table has duplicate taxon/sample IDs.")
    if metadata["SampleID"].duplicated().any():
        problems.append("Metadata has duplicate sample IDs.")
    if counts.columns.tolist() != metadata["SampleID"].tolist():
        problems.append("Count-table sample IDs/order do not match metadata.")
    values = counts.apply(pd.to_numeric, errors="coerce").to_numpy(dtype=float)
    if not np.isfinite(values).all():
        problems.append("Counts include missing/non-numeric/non-finite values.")
    elif (values < 0).any() or not np.equal(values, np.floor(values)).all():
        problems.append("Counts must be nonnegative integers.")
    elif not np.array_equal(values.sum(axis=0), metadata["LibrarySize"].to_numpy()):
        problems.append("Recorded library sizes do not equal column sums.")
    if (pd.to_numeric(metadata["LibrarySize"], errors="coerce") <= 0).any():
        problems.append("Library sizes must be positive.")
    if not set(metadata["Group"]) == {"Case", "Control"}:
        problems.append("Expected both Case and Control groups.")
    if truth is not None:
        if truth["Taxon"].tolist() != counts.index.tolist():
            problems.append("Truth table taxa/order do not match counts.")
        if not truth["True_DA"].eq(0).all():
            problems.append("A null truth table must mark all taxa non-DA.")
    return problems


def load_tables(input_dir):
    counts = pd.read_csv(input_dir / "null_counts.csv", index_col=0)
    metadata = pd.read_csv(input_dir / "null_metadata.csv")
    truth = pd.read_csv(input_dir / "null_ground_truth.csv")
    return counts, metadata, truth


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=Path("outputs"))
    args = parser.parse_args()
    problems = validate(*load_tables(args.input_dir))
    if problems:
        for item in problems:
            print(f"FAIL: {item}")
        raise SystemExit(1)
    print("PASS: counts, metadata and null truth checks.")


if __name__ == "__main__":
    main()
