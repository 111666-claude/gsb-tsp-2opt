"""旅行商：最近邻 + 2-opt，只用标准库。"""

import itertools
import math


class TspError(ValueError):
    """输入不合法。"""

    def __init__(self, message):
        super().__init__(message)
        self.message = message


def points_from_text(text):
    """解析 "0,0;10,0"。"""
    points = []
    for item in text.split(";"):
        item = item.strip()
        if not item:
            continue
        left, _, right = item.partition(",")
        try:
            point = (float(left), float(right))
        except ValueError as error:
            raise TspError("第 %d 个点坐标不合法：%s" % (len(points) + 1, item)) from error
        if not (math.isfinite(point[0]) and math.isfinite(point[1])):
            raise TspError("第 %d 个点坐标不合法：%s" % (len(points) + 1, item))
        points.append(point)
    if len(points) < 2:
        raise TspError("至少需要两个点")
    return points


def distance(first, second):
    return math.hypot(first[0] - second[0], first[1] - second[1])


def tour_length(tour, points):
    """闭合回路长度：顺次距离之和加上最后回到起点那段。"""
    total = 0.0
    for index in range(len(tour)):
        total += distance(points[tour[index]], points[tour[(index + 1) % len(tour)]])
    return total


def nearest_neighbour(points, start=0):
    """最近邻初始解。"""
    remaining = set(range(len(points)))
    tour = [start]
    remaining.discard(start)
    while remaining:
        current = tour[-1]
        nxt = min(remaining, key=lambda index: distance(points[current], points[index]))
        tour.append(nxt)
        remaining.discard(nxt)
    return tour


def two_opt(tour, points):
    """2-opt 改进：每轮用 O(1) 增益公式，反复改进到没有负增益为止。

    删除边 (a,b) 与 (c,d)，改接 (a,c) 与 (b,d)，
    增益 = d(a,c)+d(b,d)-d(a,b)-d(c,d)，只接受严格为负的增益。
    固定 tour[0] 不动，结果仍是 0..n-1 的排列。
    """
    tour = list(tour)
    n = len(tour)
    hypot = math.hypot
    moves = 0
    improved = True
    while improved:
        improved = False
        for i in range(n - 2):
            # i == 0 时 j 不能取 n-1，否则两条被删的边共用起点 0。
            last_j = n - 2 if i == 0 else n - 1
            for j in range(i + 2, last_j + 1):
                ax, ay = points[tour[i]]
                bx, by = points[tour[i + 1]]
                cx, cy = points[tour[j]]
                dx, dy = points[tour[(j + 1) % n]]
                gain = (hypot(ax - cx, ay - cy) + hypot(bx - dx, by - dy)
                        - hypot(ax - bx, ay - by) - hypot(cx - dx, cy - dy))
                if gain < -1e-12:
                    tour[i + 1:j + 1] = tour[i + 1:j + 1][::-1]
                    moves += 1
                    improved = True
    return tour, moves


def bound(points):
    """最小生成树（MST）下界：Prim，O(n^2) 时间、O(n) 额外内存。"""
    n = len(points)
    in_tree = [False] * n
    in_tree[0] = True
    best = [math.inf] * n
    for index in range(1, n):
        best[index] = distance(points[0], points[index])
    total = 0.0
    for _ in range(n - 1):
        nxt = -1
        low = math.inf
        for index in range(1, n):
            if not in_tree[index] and best[index] < low:
                low = best[index]
                nxt = index
        in_tree[nxt] = True
        total += low
        for index in range(1, n):
            if not in_tree[index]:
                d = distance(points[nxt], points[index])
                if d < best[index]:
                    best[index] = d
    return total


def optimal(points):
    """n ≤ 10 时全排列暴力最优（固定 0 号点开头）。"""
    n = len(points)
    if n > 10:
        raise TspError("暴力最优只支持 n ≤ 10，当前 n=%d" % n)
    best = math.inf
    for perm in itertools.permutations(range(1, n)):
        total = distance(points[0], points[perm[0]])
        for index in range(n - 2):
            total += distance(points[perm[index]], points[perm[index + 1]])
        total += distance(points[perm[-1]], points[0])
        if total < best:
            best = total
    return best
