# tsp-2opt

旅行商：最近邻初始解 + 2-opt 改进 + 下界/暴力对照，只用 Python 标准库。

```
python3 -m tsp2opt.cli --sample 8 --optimal --bound
python3 -m tsp2opt.cli --points '0,0;10,0;10,10;0,10'
python3 -m unittest discover -s tests -v
```

## 口径

- **2-opt**：每轮用 O(1) 增益公式 `d(a,c)+d(b,d)-d(a,b)-d(c,d)`（`(a,b)` 与 `(c,d)` 是两条被删的边），
  只接受严格为负的增益，反复改进到没有负增益为止；不每轮重算整条回路。
- **暴力最优**：`--optimal` 对 n ≤ 10 固定 0 号点开头、对其余点全排列，给最优长度与 gap；n > 10 明确报错。
- **下界**：`--bound` 用 Prim 算法给最小生成树（MST）下界，O(n²) 时间、O(n) 内存。
- 质量：`--sample 8` 与 `--sample 30` 的 2-opt 结果都 ≤ 最优 × 1.05（8 点时直接到最优 2705.539）。
- 不变量：结果是 0..n-1 的排列且固定以 0 号点开头；闭合长度等于顺次距离之和再加上最后回到起点那段；
  bound ≤ optimal ≤ 2-opt 结果；同一输入重复运行结果相同。
- 规模：n = 200 的点集 1 秒内出结果，内存 O(n)；距离按需用 `math.hypot` 计算。
- 边界：点数 < 2 或坐标非法（含 nan/inf）报错并指出是第几个点；两个点时直接给这两点往返。

## 计划新增的能力

```
--points 点集     分号分隔的 x,y
--sample N        生成 N 个固定种子的点
--optimal         额外给暴力最优与 gap
--bound           额外打印下界
```

## 输出

```
points=8 moves=2 length=2705.539
tour=0,1,6,2,5,4,3,7
bound=1961.667
optimal=2705.539 gap=0.00%
```

## 目录

```
tsp2opt/tour.py   最近邻、2-opt、下界与暴力
tsp2opt/cli.py    命令行入口
tests/            unittest 用例
```
