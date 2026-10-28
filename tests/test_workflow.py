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


if __name__ == "__main__":
    unittest.main()
