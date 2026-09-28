# tsp-2opt

旅行商：最近邻初始解 + 2-opt 改进 + 下界/暴力对照，只用 Python 标准库。

```
python3 -m tsp2opt.cli --sample 8 --optimal --bound
python3 -m tsp2opt.cli --points '0,0;10,0;10,10;0,10'
python3 -m unittest discover -s tests -v
```

## 口径（README 为准）

- **2-opt 要真的做对**：`--sample 8` 的最近邻长度是 3200.142，现在 `two_opt` 的增益公式只算了一条新边，
  换完反而变成 `length=4317.201`（比最近邻还差 35%），按口径要 `moves ≥ 1` 且长度 ≤ 最优 × 1.05 = 2840.816。
- **暴力最优与下界**：`--optimal` 对 n ≤ 10 用全排列给最优长度与 gap（现在直接报「还没实现」）；
  `--bound` 给最小生成树下界（现在恒为 0）。2-opt 的结果要 ≤ 最优 × 1.05。
- 2-opt 要求：每轮用 O(1) 的增益公式（`d(a,c)+d(b,d)-d(a,b)-d(c,d)`），反复改进到没有负增益为止；
  不许每轮重算整条回路（O(n³) 不允许），也不许接受会让回路变长的交换。
- 不变量：结果是 0..n-1 的排列且固定以 0 号点开头；闭合长度等于顺次距离之和再加上最后回到起点那段；
  下界 ≤ 最优 ≤ 2-opt 结果；同一输入重复运行结果相同。
- 规模：n = 200 的点集 1 秒内出结果，内存 O(n)；距离用一次 `math.hypot` 算完，不许反复开方比较。

## 现在的行为

- `two_opt` 的 `added` 只算 `d(tour[left-1], tour[right])`，增益公式少了一项，交换会把回路拉长
  （8 点样本从 3200.142 变成 4317.201）。
- `bound` 恒返回 0；`optimal` 直接抛 `TspError`。
- CLI 因此打印 `moves=0`，长度就是最近邻的结果。

## 计划新增的能力

```
--points 点集     分号分隔的 x,y
--sample N        生成 N 个固定种子的点
--optimal         额外给暴力最优与 gap
--bound           额外打印下界
```

## 输出

```
points=8 moves=5 length=2806.430
tour=0,3,5,7,6,4,2,1
bound=2510.333
optimal=2705.539 gap=3.73%
```

## 目录

```
tsp2opt/tour.py   最近邻、2-opt、下界与暴力
tsp2opt/cli.py    命令行入口
tests/            unittest 用例
```
