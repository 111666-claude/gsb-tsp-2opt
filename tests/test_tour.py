import math
import time
import unittest

from tsp2opt.cli import sample
from tsp2opt.tour import (TspError, bound, distance, nearest_neighbour, optimal,
                          points_from_text, tour_length, two_opt)

SQUARE = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]


class ParseTest(unittest.TestCase):
    def test_two_points(self):
        self.assertEqual(points_from_text("0,0;3,4"), [(0.0, 0.0), (3.0, 4.0)])

    def test_bad_point_reports_index(self):
        with self.assertRaises(TspError) as context:
            points_from_text("0,0;x,4")
        self.assertEqual(context.exception.index, 1)
        self.assertIn("第 2 个点", str(context.exception))

    def test_missing_comma_reports_index(self):
        with self.assertRaises(TspError) as context:
            points_from_text("0,0;1;2,3")
        self.assertEqual(context.exception.index, 1)

    def test_non_finite_reports_index(self):
        for text in ("0,0;1,nan", "0,0;inf,3", "0,0;2,-inf"):
            with self.subTest(text=text), self.assertRaises(TspError) as context:
                points_from_text(text)
            self.assertEqual(context.exception.index, 1)

    def test_too_few(self):
        for text in ("", "0,0", ";;;"):
            with self.subTest(text=text), self.assertRaises(TspError):
                points_from_text(text)


class TourTest(unittest.TestCase):
    def test_nearest_neighbour_is_permutation(self):
        tour = nearest_neighbour(SQUARE)
        self.assertEqual(sorted(tour), [0, 1, 2, 3])
        self.assertEqual(tour[0], 0)

    def test_square_length(self):
        self.assertAlmostEqual(tour_length(nearest_neighbour(SQUARE), SQUARE), 40.0, places=6)

    def test_two_points_round_trip(self):
        points = [(0.0, 0.0), (3.0, 4.0)]
        tour, moves = two_opt(nearest_neighbour(points), points)
        self.assertEqual(tour, [0, 1])
        self.assertEqual(moves, 0)
        self.assertAlmostEqual(tour_length(tour, points), 10.0, places=9)

    def test_two_opt_keeps_permutation(self):
        tour, moves = two_opt(nearest_neighbour(SQUARE), SQUARE)
        self.assertEqual(sorted(tour), [0, 1, 2, 3])
        self.assertEqual(tour[0], 0)
        self.assertEqual(moves, 0)

    def test_two_opt_on_line(self):
        points = [(float(i), 0.0) for i in range(5)]
        tour, _ = two_opt(nearest_neighbour(points), points)
        self.assertAlmostEqual(tour_length(tour, points), 8.0, places=6)

    def test_two_opt_gain_formula_needs_both_new_edges(self):
        # 0 出发的 NN 回路 0-1-3-2 有一次交叉；旧公式只看 d(0,3) 一条新边
        # （14.14 < 10+10=20 会误接受为“更短”），正确公式
        # d(0,2)+d(1,3)-d(0,1)-d(2,3) = 10+2-10-10 = -8，必须接受。
        points = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
        tour, moves = two_opt([0, 1, 3, 2], points)
        self.assertEqual(moves, 1)
        self.assertAlmostEqual(tour_length(tour, points), 40.0, places=9)
        self.assertEqual(sorted(tour), [0, 1, 2, 3])

    def test_two_opt_never_lengthens(self):
        # 构造一个“只加一条新边看似赚、加两条其实亏”的局面，正确公式必须拒绝。
        points = [(0.0, 0.0), (10.0, 0.0), (10.0, 1.0), (9.0, 1.0)]
        initial = [0, 1, 2, 3]
        before = tour_length(initial, points)
        tour, moves = two_opt(initial, points)
        self.assertEqual(moves, 0)
        self.assertEqual(tour, initial)
        self.assertAlmostEqual(tour_length(tour, points), before, places=9)

    def test_two_opt_reaches_local_optimum(self):
        # 圆周上的点按星形顺序给初始回路，交叉多、需要连续多轮才消干净
        points = [(math.cos(k * math.pi / 4), math.sin(k * math.pi / 4))
                  for k in range(8)]
        initial = [0, 2, 4, 6, 1, 3, 5, 7]
        tour, moves = two_opt(initial, points)
        self.assertGreater(moves, 0)
        count = len(tour)
        for left in range(1, count):
            a, b = tour[left - 1], tour[left]
            for right in range(left + 1, count + 1):
                c, d = tour[right - 1], tour[right % count]
                delta = (distance(points[a], points[c]) + distance(points[b], points[d])
                         - distance(points[a], points[b]) - distance(points[c], points[d]))
                self.assertGreaterEqual(delta, -1e-9)

    def test_deterministic(self):
        points = sample(8)
        first, moves_first = two_opt(nearest_neighbour(points), points)
        second, moves_second = two_opt(nearest_neighbour(points), points)
        self.assertEqual(first, second)
        self.assertEqual(moves_first, moves_second)

    def test_sample8_quality(self):
        points = sample(8)
        tour, _ = two_opt(nearest_neighbour(points), points)
        length = tour_length(tour, points)
        self.assertAlmostEqual(optimal(points), 2705.539, places=3)
        self.assertLessEqual(length, optimal(points) * 1.05 + 1e-9)


class BoundTest(unittest.TestCase):
    def test_mst_square(self):
        self.assertAlmostEqual(bound(SQUARE), 30.0, places=9)

    def test_mst_two_points(self):
        self.assertAlmostEqual(bound([(0.0, 0.0), (3.0, 4.0)]), 5.0, places=9)

    def test_bound_not_zero_and_ordering(self):
        points = sample(8)
        tour, _ = two_opt(nearest_neighbour(points), points)
        value = bound(points)
        best = optimal(points)
        self.assertGreater(value, 0.0)
        self.assertLessEqual(value, best + 1e-9)
        self.assertLessEqual(best, tour_length(tour, points) + 1e-9)

    def test_bound_equals_brute_mst(self):
        # 用枚举生成树的方式交叉验证 Prim
        import itertools
        points = sample(7)
        count = len(points)
        matrix = [[distance(points[i], points[j]) for j in range(count)]
                  for i in range(count)]
        # 枚举所有 n-1 条边的子集，用并查集判树
        total_edges = [(i, j) for i in range(count) for j in range(i + 1, count)]
        brute = math.inf
        for subset in itertools.combinations(total_edges, count - 1):
            parent = list(range(count))

            def find(x):
                while parent[x] != x:
                    parent[x] = parent[parent[x]]
                    x = parent[x]
                return x

            weight = 0.0
            ok = True
            for i, j in subset:
                ri, rj = find(i), find(j)
                if ri == rj:
                    ok = False
                    break
                parent[ri] = rj
                weight += matrix[i][j]
            if ok:
                brute = min(brute, weight)
        self.assertAlmostEqual(bound(points), brute, places=9)


class OptimalTest(unittest.TestCase):
    def test_square_optimal(self):
        self.assertAlmostEqual(optimal(SQUARE), 40.0, places=9)

    def test_two_points_optimal(self):
        self.assertAlmostEqual(optimal([(0.0, 0.0), (3.0, 4.0)]), 10.0, places=9)

    def test_optimal_sample8(self):
        self.assertAlmostEqual(optimal(sample(8)), 2705.539, places=3)

    def test_optimal_matches_exhaustive_tours(self):
        import itertools
        points = sample(6)
        count = len(points)
        brute = math.inf
        for rest in itertools.permutations(range(1, count)):
            brute = min(brute, tour_length((0,) + rest, points))
        self.assertAlmostEqual(optimal(points), brute, places=9)

    def test_optimal_rejects_n_gt_10(self):
        with self.assertRaises(TspError):
            optimal(sample(11))

    def test_optimal_rejects_too_few_points(self):
        with self.assertRaises(TspError):
            optimal([(0.0, 0.0)])


class ScaleTest(unittest.TestCase):
    def test_n200_under_one_second(self):
        points = sample(200)
        start = time.perf_counter()
        tour, _ = two_opt(nearest_neighbour(points), points)
        elapsed = time.perf_counter() - start
        self.assertLess(elapsed, 1.0)
        self.assertEqual(sorted(tour), list(range(200)))
        self.assertEqual(tour[0], 0)
        self.assertLessEqual(bound(points), tour_length(tour, points) + 1e-9)


if __name__ == "__main__":
    unittest.main()
