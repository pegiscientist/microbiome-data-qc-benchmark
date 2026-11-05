"""Validate basic integrity of a synthetic microbiome count table."""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def validate(counts, metadata, truth=None):
    """Return a list of input-integrity problems for the demonstration."""
    problems = []
    required_metadata = {"SampleID", "Group", "LibrarySize"}

    if counts.empty or metadata.empty:
        problems.append("Counts and metadata must not be empty.")
    if not counts.index.is_unique or not counts.columns.is_unique:
        problems.append("Count table has duplicate taxon/sample IDs.")

    missing_metadata = sorted(required_metadata - set(metadata.columns))
    if missing_metadata:
        problems.append(f"Missing metadata columns: {', '.join(missing_metadata)}.")
    else:
        ids = metadata["SampleID"]
        if ids.isna().any() or ids.duplicated().any():
            problems.append("Metadata has missing or duplicate sample IDs.")
        if counts.columns.tolist() != ids.tolist():
            problems.append("Count-table sample IDs/order do not match metadata.")

        sizes = pd.to_numeric(metadata["LibrarySize"], errors="coerce").to_numpy(dtype=float)
        if not np.isfinite(sizes).all() or (sizes <= 0).any():
            problems.append("Library sizes must be finite positive numbers.")

        groups = metadata["Group"]
        if groups.isna().any() or set(groups) != {"Case", "Control"}:
            problems.append("Expected both Case and Control groups without missing labels.")

    values = counts.apply(pd.to_numeric, errors="coerce").to_numpy(dtype=float)
    if not np.isfinite(values).all():
        problems.append("Counts include missing/non-numeric/non-finite values.")
    elif (values < 0).any() or not np.equal(values, np.floor(values)).all():
        problems.append("Counts must be nonnegative integers.")
    elif not missing_metadata:
        sizes = pd.to_numeric(metadata["LibrarySize"], errors="coerce").to_numpy(dtype=float)
        if np.isfinite(sizes).all() and not np.array_equal(values.sum(axis=0), sizes):
            problems.append("Recorded library sizes do not equal column sums.")

    if truth is not None:
        missing_truth = sorted({"Taxon", "True_DA"} - set(truth.columns))
        if missing_truth:
            problems.append(f"Missing truth columns: {', '.join(missing_truth)}.")
        else:
            if truth["Taxon"].isna().any() or truth["Taxon"].duplicated().any():
                problems.append("Truth table has missing or duplicate taxa.")
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
