"""命令行入口：算一条旅行商回路。"""

import argparse
import sys

from .tour import (TspError, bound, nearest_neighbour, optimal, points_from_text,
                   tour_length, two_opt)


def sample(count):
    """固定种子的点集。"""
    points = []
    state = 20260928
    for _ in range(count):
        state = (state * 6364136223846793005 + 1442695040888963407) % (2 ** 64)
        x = (state >> 40) % 1000
        state = (state * 6364136223846793005 + 1442695040888963407) % (2 ** 64)
        y = (state >> 40) % 1000
        points.append((float(x), float(y)))
    return points


def build_parser():
    parser = argparse.ArgumentParser(prog="tsp-2opt", description="旅行商：最近邻 + 2-opt")
    parser.add_argument("--points", help="分号分隔的 x,y")
    parser.add_argument("--sample", type=int, help="生成 N 个固定种子的点")
    parser.add_argument("--optimal", action="store_true", help="额外用暴力给最优（n ≤ 10）")
    parser.add_argument("--bound", action="store_true", help="额外打印下界")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        points = points_from_text(args.points) if args.points else sample(args.sample or 8)
        initial = nearest_neighbour(points)
        improved, moves = two_opt(initial, points)
        length = tour_length(improved, points)
        print("points=%d moves=%d length=%.3f" % (len(points), moves, length))
        print("tour=%s" % ",".join(str(index) for index in improved))
        if args.bound:
            print("bound=%.3f" % bound(points))
        if args.optimal:
            best = optimal(points)
            print("optimal=%.3f gap=%.2f%%" % (best, (length / best - 1) * 100))
    except (TspError, ValueError) as error:
        print("错误：%s" % error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
