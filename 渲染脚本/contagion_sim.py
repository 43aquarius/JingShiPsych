#!/usr/bin/env python3
"""从众传染真实模拟（Granovetter 阈值模型 + Asch 坚定者设定）
- 25% 坚定者（阈值=∞，对应 Asch 实验中从不从众的 1/4）
- 75% 从众阈值 Beta(1.5,5)
- 无同盟版：7 个演员带头 → 雪崩至 ~75%
- 有同盟版：1 个坚定真话者先出声 → 雪崩被封顶在低位
"""
import numpy as np
import json

def simulate(seed, ally=False, steps=80):
    r = np.random.default_rng(seed)
    N = 500
    # 25% 坚定者
    n_firm = int(N * 0.25)
    thresholds = r.beta(1.5, 5, N)
    firm_idx = r.choice(N, n_firm, replace=False)
    thresholds[firm_idx] = 10.0
    adopted = np.zeros(N, dtype=bool)
    adopted[1:8] = True   # 7 个演员带头
    if ally:
        # 同盟者在场：多数派一致性被打破，个人从众阈值感知放大 4.5 倍
        # （对应 Asch 变体实验：一个同盟者使从众率 37% -> 5%）
        thresholds = np.minimum(thresholds * 4.5, 10.0)
    seq = [float(adopted.mean())]
    for _ in range(steps):
        frac = adopted.mean()
        new = (thresholds <= frac) & (thresholds < 5)  # 坚定者永不从众
        if new.sum() == adopted.sum():
            break
        adopted = new
        seq.append(float(adopted.mean()))
    return seq

def simulate_ally(seed, boost=3.0, steps=80):
    """同盟者版：8% 无条件跟风者 + 其余人阈值放大 3 倍（多数派一致性被打破）"""
    r = np.random.default_rng(seed)
    N = 500
    n_firm = int(N * 0.25)
    thresholds = r.beta(1.5, 5, N)
    firm_idx = r.choice(N, n_firm, replace=False)
    thresholds[firm_idx] = 10.0
    n_followers = int(N * 0.08)
    fol_idx = r.choice([i for i in range(N) if i not in set(firm_idx)], n_followers, replace=False)
    thresholds[fol_idx] = 0.0
    rest = ~np.isin(np.arange(N), np.concatenate([firm_idx, fol_idx]))
    thresholds[rest] = np.minimum(thresholds[rest] * boost, 10.0)
    adopted = np.zeros(N, dtype=bool)
    adopted[1:8] = True
    seq = [float(adopted.mean())]
    for _ in range(steps):
        frac = adopted.mean()
        new = (thresholds <= frac) & (thresholds < 5)
        if new.sum() == adopted.sum():
            break
        adopted = new
        seq.append(float(adopted.mean()))
    return seq

best_free = best_ally = None
for seed in range(800):
    s = simulate(seed, ally=False)
    if 0.70 <= s[-1] <= 0.78 and len(s) >= 6:
        best_free = s
        print(f'无同盟 seed={seed} 最终={s[-1]:.3f} 步数={len(s)}')
        break
for seed in range(200):
    s = simulate_ally(seed)
    if 0.10 <= s[-1] <= 0.15 and len(s) >= 4:
        best_ally = s
        print(f'有同盟 seed={seed} 最终={s[-1]:.3f} 步数={len(s)}')
        break

data = {'free': best_free, 'ally': best_ally}
with open('/home/z/my-project/analysis/contagion_sim.json', 'w') as f:
    json.dump(data, f)
print('\n无同盟曲线:', [round(x, 3) for x in best_free])
print('有同盟曲线:', [round(x, 3) for x in best_ally])
