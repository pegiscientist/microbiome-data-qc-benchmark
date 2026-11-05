"""Lightweight tests for synthetic simulation and data integrity checks."""
import unittest

from scripts.simulate_null import simulate
from scripts.validate_counts import validate


class TestWorkflow(unittest.TestCase):
    def setUp(self):
        self.counts, self.metadata, self.truth = simulate(seed=42)

    def test_shape_and_null_truth(self):
        self.assertEqual(self.counts.shape, (60, 40))
        self.assertEqual(int(self.truth["True_DA"].sum()), 0)
        self.assertEqual(set(self.metadata["Group"]), {"Control", "Case"})

    def test_valid_dataset_passes(self):
        self.assertEqual(validate(self.counts, self.metadata, self.truth), [])

    def test_reproducible_with_fixed_seed(self):
        again, _, _ = simulate(seed=42)
        self.assertTrue(self.counts.equals(again))

    def test_misaligned_metadata_fails(self):
        swapped = self.metadata.iloc[::-1].reset_index(drop=True)
        self.assertTrue(any("sample IDs/order" in p for p in
                            validate(self.counts, swapped, self.truth)))

    def test_library_size_corruption_fails(self):
        broken = self.metadata.copy()
        broken.loc[0, "LibrarySize"] += 1
        self.assertTrue(any("library sizes" in p for p in
                            validate(self.counts, broken, self.truth)))

    def test_missing_metadata_column_reports_problem(self):
        broken = self.metadata.drop(columns=["LibrarySize"])
        problems = validate(self.counts, broken, self.truth)
        self.assertTrue(any("Missing metadata columns" in p for p in problems))

    def test_missing_library_size_reports_problem(self):
        broken = self.metadata.copy()
        broken.loc[0, "LibrarySize"] = float("nan")
        problems = validate(self.counts, broken, self.truth)
        self.assertTrue(any("finite positive" in p for p in problems))

    def test_non_numeric_library_size_reports_problem(self):
        broken = self.metadata.copy()
        broken["LibrarySize"] = broken["LibrarySize"].astype(object)
        broken.loc[0, "LibrarySize"] = "unknown"
        problems = validate(self.counts, broken, self.truth)
        self.assertTrue(any("finite positive" in p for p in problems))

    def test_missing_truth_column_reports_problem(self):
        broken = self.truth.drop(columns=["True_DA"])
        problems = validate(self.counts, self.metadata, broken)
        self.assertTrue(any("Missing truth columns" in p for p in problems))

    def test_missing_group_label_reports_problem(self):
        broken = self.metadata.copy()
        broken.loc[0, "Group"] = None
        problems = validate(self.counts, broken, self.truth)
        self.assertTrue(any("missing labels" in p for p in problems))


if __name__ == "__main__":
    unittest.main()
