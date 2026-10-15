#!/usr/bin/env python3
"""把 Granovetter 阈值模拟曲线映射为 20x10 网格的逐点翻转时刻表
- free: 无同盟，13 步雪崩到 75%（150/200 点变红）
- ally: 放入 1 名同盟者，波前停在其防线前，封顶 11.4%（23 点）
输出: analysis/infection_grid.json
"""
import json, random

rnd = random.Random(20241015)
COLS, ROWS = 20, 10
SEED = (2, 4)      # 第一个附和者位置（左侧）
ALLY = (9, 5)      # 同盟者位置（防线靠左，让火线贴着同盟视觉更直观)

curves = json.load(open('/home/z/my-project/analysis/contagion_sim.json'))
FREE, ALLY_CURVE = curves['free'], curves['ally']
N = COLS * ROWS

def L(p, q):  # 曼哈顿距离 = 波前层数
    return abs(p[0]-q[0]) + abs(p[1]-q[1])

dots_all = [(x, y) for y in range(ROWS) for x in range(COLS)]

def build(curve, candidates, final_n):
    """按 L(seed)+噪声 排序作为翻转顺序，映射到曲线步数"""
    counts = [round(c*N) for c in curve]          # 每步结束时的累计红点数
    scored = sorted(candidates, key=lambda p: L(p, SEED) + rnd.uniform(0, 2.4))
    out = []
    for r, p in enumerate(scored):
        if r >= final_n:
            break
        k = next(i for i, c in enumerate(counts) if r < c)
        out.append({'x': p[0], 'y': p[1], 'step': k,
                    'off': round(rnd.uniform(0.15, 0.85), 3)})
    return out

# --- free：全部 200 点参与，最终 150 红 ---
free_final = round(FREE[-1] * N)
free_dots = build(FREE, dots_all, free_final)

# --- ally：受同盟庇护的点（离同盟比离感染源近 2 层以上）永不翻转 ---
protected = {p for p in dots_all if L(p, ALLY) < L(p, SEED) + 2}
cand = [p for p in dots_all if p not in protected]
ally_final = round(ALLY_CURVE[-1] * N)
ally_dots = build(ALLY_CURVE, cand, ally_final)

data = {
    'free': {'dots': free_dots, 'steps': len(FREE), 'final': FREE[-1],
             'seed': list(SEED), 'n_final': free_final},
    'ally': {'dots': ally_dots, 'steps': len(ALLY_CURVE), 'final': ALLY_CURVE[-1],
             'ally': list(ALLY), 'n_final': ally_final,
             'n_protected': len(protected)},
}
out = '/home/z/my-project/analysis/infection_grid.json'
json.dump(data, open(out, 'w'), ensure_ascii=False, indent=1)
print(f'free: {len(free_dots)} 红点 / {free_final} 目标, 13 步')
print(f'ally: {len(ally_dots)} 红点 / {ally_final} 目标, {len(ALLY_CURVE)} 步, 庇护 {len(protected)} 点')
xs = sorted({d["x"] for d in ally_dots})
print(f'ally 版红点分布列: {xs}')
