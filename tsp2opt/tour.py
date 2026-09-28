"""旅行商：最近邻 + 2-opt，只用标准库。

2-opt 用 O(1) 的增益公式 d(a,c)+d(b,d)-d(a,b)-d(c,d)，
反复交换直到没有负增益；下界取 MST；n <= 10 可全排列暴力最优。
"""

import itertools
import math


class TspError(ValueError):
    """输入不合法。"""

    def __init__(self, message, index=None):
        if index is not None:
            message = "第 %d 个点：%s" % (index + 1, message)
        super().__init__(message)
        self.message = message
        self.index = index


def points_from_text(text):
    """解析 "0,0;10,0"，坐标非法时指出是第几个点。"""
    points = []
    for item in text.split(";"):
        item = item.strip()
        if not item:
            continue
        left, sep, right = item.partition(",")
        if not sep:
            raise TspError("坐标应为 x,y 格式：%s" % item, len(points))
        try:
            x_coord = float(left)
            y_coord = float(right)
        except ValueError as error:
            raise TspError("坐标不合法：%s" % item, len(points)) from error
        if not (math.isfinite(x_coord) and math.isfinite(y_coord)):
            raise TspError("坐标必须是有限数：%s" % item, len(points))
        points.append((x_coord, y_coord))
    _check_count(points)
    return points


def _check_count(points):
    if len(points) < 2:
        raise TspError("至少需要两个点（当前 %d 个）" % len(points))


def distance(first, second):
    return math.hypot(first[0] - second[0], first[1] - second[1])


def tour_length(tour, points):
    """闭合回路长度：顺次距离加上最后回到起点那段。"""
    total = 0.0
    for index in range(len(tour)):
        total += distance(points[tour[index]], points[tour[(index + 1) % len(tour)]])
    return total


def nearest_neighbour(points, start=0):
    """最近邻初始解，固定以 start（默认 0）开头。"""
    _check_count(points)
    count = len(points)
    unvisited = [True] * count
    tour = [start]
    unvisited[start] = False
    current = start
    while len(tour) < count:
        best = -1
        best_sq = math.inf
        cx, cy = points[current]
        for index in range(count):
            if not unvisited[index]:
                continue
            px, py = points[index]
            sq = (cx - px) ** 2 + (cy - py) ** 2
            if sq < best_sq:
                best_sq = sq
                best = index
        tour.append(best)
        unvisited[best] = False
        current = best
    return tour


def two_opt(tour, points):
    """2-opt 局部最优。

    被删的两条边是 (a,b)=(left-1,left) 和 (c,d)=(right-1,right % n)，
    增量 delta = d(a,c)+d(b,d)-d(a,b)-d(c,d)；只接受 delta < 0 的交换，
    反复扫描直到整轮没有负增益。边长按当前回路缓存为 O(n)，每次候选 O(1)。
    """
    _check_count(points)
    tour = list(tour)
    count = len(tour)
    if count < 3:
        return tour, 0

    edge = [distance(points[tour[i]], points[tour[(i + 1) % count]])
            for i in range(count)]
    moves = 0
    left = 1
    while left < count:
        node_a = tour[left - 1]
        node_b = tour[left]
        remove_ab = edge[left - 1]
        pa = points[node_a]
        pb = points[node_b]
        swapped = False
        for right in range(left + 1, count + 1):
            node_c = tour[right - 1]
            node_d = tour[right % count]
            removed = remove_ab + edge[right - 1]
            delta = (distance(pa, points[node_c])
                     + distance(pb, points[node_d]) - removed)
            if delta < -1e-12 * removed:
                tour[left:right] = reversed(tour[left:right])
                edge[left:right - 1] = reversed(edge[left:right - 1])
                edge[left - 1] = distance(pa, points[node_c])
                edge[right - 1] = distance(pb, points[node_d])
                moves += 1
                left = 1
                swapped = True
                break
        if not swapped:
            left += 1
    return tour, moves


def bound(points):
    """MST 下界：最小生成树权值不超过任何哈密顿回路的长度。"""
    _check_count(points)
    count = len(points)
    closest = [math.inf] * count
    in_tree = [False] * count
    closest[0] = 0.0
    total = 0.0
    for _ in range(count):
        node = -1
        best = math.inf
        for candidate in range(count):
            if not in_tree[candidate] and closest[candidate] < best:
                best = closest[candidate]
                node = candidate
        in_tree[node] = True
        total += best if node != 0 else 0.0
        px, py = points[node]
        for other in range(count):
            if in_tree[other]:
                continue
            ox, oy = points[other]
            weight = math.hypot(px - ox, py - oy)
            if weight < closest[other]:
                closest[other] = weight
    return total


def optimal(points):
    """全排列暴力最优，仅支持 n <= 10；n > 10 明确报错。"""
    _check_count(points)
    count = len(points)
    if count > 10:
        raise TspError("暴力最优只支持 n <= 10（当前 n=%d）" % count)
    matrix = [[0.0] * count for _ in range(count)]
    for i in range(count):
        for j in range(i + 1, count):
            matrix[i][j] = matrix[j][i] = distance(points[i], points[j])
    best = math.inf
    for rest in itertools.permutations(range(1, count)):
        tour = (0,) + rest
        total = 0.0
        for i in range(count):
            total += matrix[tour[i]][tour[(i + 1) % count]]
        if total < best:
            best = total
    return best
