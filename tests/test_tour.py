import unittest

from tsp2opt.tour import (TspError, nearest_neighbour, points_from_text, tour_length,
                          two_opt)

SQUARE = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]


class ParseTest(unittest.TestCase):
    def test_two_points(self):
        self.assertEqual(points_from_text("0,0;3,4"), [(0.0, 0.0), (3.0, 4.0)])

    def test_bad_point(self):
        with self.assertRaises(TspError):
            points_from_text("0,0;x,4")

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
        tour, _ = two_opt(nearest_neighbour(SQUARE), SQUARE)
        self.assertEqual(sorted(tour), [0, 1, 2, 3])

    def test_two_opt_on_line(self):
        points = [(0.0, 0.0), (1.0, 0.0), (2.0, 0.0), (3.0, 0.0), (4.0, 0.0)]
        tour, _ = two_opt(nearest_neighbour(points), points)
        self.assertAlmostEqual(tour_length(tour, points), 8.0, places=6)


if __name__ == "__main__":
    unittest.main()
