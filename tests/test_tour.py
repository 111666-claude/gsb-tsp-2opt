import math
import time
import unittest

from tsp2opt.cli import sample
from tsp2opt.tour import (TspError, bound, nearest_neighbour, optimal,
                          points_from_text, tour_length, two_opt)

SQUARE = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]


class ParseTest(unittest.TestCase):
    def test_two_points(self):
        self.assertEqual(points_from_text("0,0;3,4"), [(0.0, 0.0), (3.0, 4.0)])

    def test_bad_point(self):
        with self.assertRaises(TspError) as context:
            points_from_text("0,0;x,4")
        self.assertIn("第 2 个点", str(context.exception))

    def test_non_finite_point(self):
        with self.assertRaises(TspError) as context:
            points_from_text("0,0;1,nan")
        self.assertIn("第 2 个点", str(context.exception))

    def test_too_few(self):
        with self.assertRaises(TspError):
            points_from_text("0,0")


class TourTest(unittest.TestCase):
    def test_nearest_neighbour_is_permutation(self):
        tour = nearest_neighbour(SQUARE)
        self.assertEqual(sorted(tour), [0, 1, 2, 3])
        self.assertEqual(tour[0], 0)

    def test_square_length(self):
        tour = nearest_neighbour(SQUARE)
        self.assertAlmostEqual(tour_length(tour, SQUARE), 40.0, places=6)

    def test_two_opt_keeps_permutation(self):
        tour, moves = two_opt(nearest_neighbour(SQUARE), SQUARE)
        self.assertEqual(sorted(tour), [0, 1, 2, 3])
        self.assertEqual(tour[0], 0)
        self.assertGreaterEqual(moves, 0)

    def test_two_opt_on_line(self):
        points = [(0.0, 0.0), (1.0, 0.0), (2.0, 0.0), (3.0, 0.0), (4.0, 0.0)]
        tour, _ = two_opt(nearest_neighbour(points), points)
        self.assertAlmostEqual(tour_length(tour, points), 8.0, places=6)

    def test_two_points_round_trip(self):
        points = [(0.0, 0.0), (3.0, 4.0)]
        tour = nearest_neighbour(points)
        self.assertEqual(tour, [0, 1])
        improved, moves = two_opt(tour, points)
        self.assertEqual(improved, [0, 1])
        self.assertEqual(moves, 0)
        self.assertAlmostEqual(tour_length(improved, points), 10.0, places=6)


class TwoOptGainTest(unittest.TestCase):
    def test_never_lengthens_and_is_local_optimum(self):
        for count in (4, 5, 6, 8, 10):
            points = sample(count)
            initial = nearest_neighbour(points)
            before = tour_length(initial, points)
            improved, moves = two_opt(initial, points)
            after = tour_length(improved, points)
            self.assertLessEqual(after, before + 1e-9)
            self.assertEqual(sorted(improved), list(range(count)))
            self.assertEqual(improved[0], 0)
            # 收敛后任何 2-opt 交换都不能再有负增益。
            tour = improved
            n = len(tour)
            for i in range(n - 2):
                last_j = n - 2 if i == 0 else n - 1
                for j in range(i + 2, last_j + 1):
                    a, b = points[tour[i]], points[tour[i + 1]]
                    c, d = points[tour[j]], points[tour[(j + 1) % n]]
                    gain = (_dist(a, c) + _dist(b, d) - _dist(a, b) - _dist(c, d))
                    self.assertGreaterEqual(gain, -1e-9)

    def test_sample8_quality(self):
        points = sample(8)
        best = optimal(points)
        self.assertAlmostEqual(best, 2705.539, places=3)
        improved, moves = two_opt(nearest_neighbour(points), points)
        length = tour_length(improved, points)
        self.assertGreaterEqual(moves, 1)
        self.assertLessEqual(length, best * 1.05)
        self.assertAlmostEqual(length, 2705.539, places=3)

    def test_deterministic(self):
        points = sample(8)
        first, moves1 = two_opt(nearest_neighbour(points), points)
        second, moves2 = two_opt(nearest_neighbour(points), points)
        self.assertEqual(first, second)
        self.assertEqual(moves1, moves2)

    def test_sample30_quality(self):
        points = sample(30)
        # n > 10 无法暴力；以 30 个不同起点 2-opt 的最好结果作强参考。
        reference = min(
            tour_length(two_opt(nearest_neighbour(points, start), points)[0], points)
            for start in range(len(points)))
        improved, _ = two_opt(nearest_neighbour(points), points)
        self.assertLessEqual(tour_length(improved, points), reference * 1.05)


class BoundTest(unittest.TestCase):
    def test_mst_square(self):
        self.assertAlmostEqual(bound(SQUARE), 30.0, places=6)

    def test_bound_below_optimal_and_tour(self):
        for count in (4, 5, 8):
            points = sample(count)
            lower = bound(points)
            best = optimal(points)
            length = tour_length(two_opt(nearest_neighbour(points), points)[0], points)
            self.assertLessEqual(lower, best + 1e-9)
            self.assertLessEqual(best, length + 1e-9)


class OptimalTest(unittest.TestCase):
    def test_square_optimal(self):
        self.assertAlmostEqual(optimal(SQUARE), 40.0, places=6)

    def test_two_points_optimal(self):
        self.assertAlmostEqual(optimal([(0.0, 0.0), (3.0, 4.0)]), 10.0, places=6)

    def test_too_large(self):
        with self.assertRaises(TspError):
            optimal(sample(11))


class ScaleTest(unittest.TestCase):
    def test_n200_within_one_second(self):
        points = sample(200)
        start = time.perf_counter()
        improved, _ = two_opt(nearest_neighbour(points), points)
        elapsed = time.perf_counter() - start
        self.assertEqual(sorted(improved), list(range(200)))
        self.assertLess(elapsed, 1.0)
        self.assertAlmostEqual(bound(points), bound(points), places=6)


def _dist(first, second):
    return math.hypot(first[0] - second[0], first[1] - second[1])


if __name__ == "__main__":
    unittest.main()
