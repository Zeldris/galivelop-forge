"""0.1.0-6: deterministic partitions (invariant 3)."""
import random
import unittest

from gforge.splits import TEST, TRAIN, VAL, Split, SplitError, bucket, partition_of, split, verify

IDS = ["ex-{}".format(i) for i in range(2000)]


class SplitTests(unittest.TestCase):
    def test_two_runs_are_identical_and_order_does_not_matter(self):
        shuffled = list(IDS)
        random.Random(7).shuffle(shuffled)
        self.assertEqual(split(IDS, "s1"), split(IDS, "s1"))
        self.assertEqual(split(IDS, "s1"), split(shuffled, "s1"))

    def test_test_never_appears_in_train_and_nothing_is_lost(self):
        result = split(IDS, "s1")
        self.assertFalse(set(result.test) & set(result.train))
        self.assertFalse(set(result.test) & set(result.val))
        self.assertFalse(set(result.val) & set(result.train))
        self.assertEqual(sorted(result.train + result.val + result.test), sorted(IDS))

    def test_other_seed_gives_other_partition(self):
        self.assertNotEqual(split(IDS, "s1").test, split(IDS, "s2").test)
        self.assertEqual(split(IDS, 5), split(IDS, "5"))

    def test_fractions_are_respected_roughly(self):
        result = split(IDS, "s1", val=0.2, test=0.1)
        self.assertAlmostEqual(len(result.test) / len(IDS), 0.1, delta=0.03)
        self.assertAlmostEqual(len(result.val) / len(IDS), 0.2, delta=0.03)

    def test_adding_examples_never_moves_an_old_one(self):
        small = split(IDS[:500], "s1")
        big = split(IDS, "s1")
        for name in (TRAIN, VAL, TEST):
            self.assertLessEqual(set(small.part(name)), set(big.part(name)))
        self.assertEqual(partition_of("s1", IDS[3]), next(n for n in (TRAIN, VAL, TEST) if IDS[3] in big.part(n)))

    def test_zero_test_fraction_keeps_test_empty(self):
        self.assertEqual(split(IDS, "s1", val=0.1, test=0).test, ())

    def test_duplicate_id_is_rejected_with_its_id(self):
        with self.assertRaisesRegex(SplitError, "duplicate example id 'a'"):
            split(["a", "b", "a"], "s1")

    def test_bad_inputs_are_rejected_with_the_reason(self):
        with self.assertRaisesRegex(SplitError, "seed must be"):
            split(IDS, "")
        with self.assertRaisesRegex(SplitError, "seed must be"):
            split(IDS, None)
        with self.assertRaisesRegex(SplitError, "non-empty string"):
            split([""], "s1")
        with self.assertRaisesRegex(SplitError, "val fraction"):
            split(IDS, "s1", val=-0.1)
        with self.assertRaisesRegex(SplitError, "room for train"):
            split(IDS, "s1", val=0.5, test=0.5)

    def test_verify_catches_a_leak_from_test_into_train(self):
        leaked = Split("s", 0.1, 0.1, ("a", "b"), (), ("b",))
        with self.assertRaisesRegex(SplitError, "both train and test"):
            verify(leaked)

    def test_bucket_validates_seed(self):
        with self.assertRaisesRegex(SplitError, "seed must be a non-empty string"):
            bucket("", "ex-1")
        self.assertEqual(bucket(7, "ex-1"), bucket("7", "ex-1"))


if __name__ == "__main__":
    unittest.main()
