"""旅行商：最近邻 + 2-opt，只用标准库。

缺陷：two_opt 只扫一轮，增益公式还只算了一条新边；下界恒为 0，暴力最优没实现。
"""

import math


class TspError(ValueError):
    """输入不合法。缺陷：不带位置。"""

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
            points.append((float(left), float(right)))
        except ValueError as error:
            raise TspError("坐标不合法：%s" % item) from error
    if len(points) < 2:
        raise TspError("至少需要两个点")
    return points


def distance(first, second):
    return math.hypot(first[0] - second[0], first[1] - second[1])


def tour_length(tour, points):
    """闭合回路长度。"""
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
    """缺陷：只扫一轮，而且增益里只算了一条新边，多数改进会被拒掉。"""
    tour = list(tour)
    changed = 0
    for left in range(1, len(tour) - 1):
        for right in range(left + 1, len(tour)):
            removed = (distance(points[tour[left - 1]], points[tour[left]])
                       + distance(points[tour[right - 1]], points[tour[right]]))
            added = distance(points[tour[left - 1]], points[tour[right]])
            if added < removed:
                tour[left:right] = reversed(tour[left:right])
                changed += 1
    return tour, changed


def bound(points):
    """缺陷：下界直接返回 0。"""
    return 0.0


def optimal(points):
    """缺陷：还没实现。"""
    raise TspError("暴力最优还没实现")
