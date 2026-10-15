#!/usr/bin/env python3
"""分析 BGM 的能量包络与节拍点，输出能量曲线和节拍时间列表"""
import subprocess, json, struct, wave, sys

# 先转成 22050Hz 单声道 wav 便于分析
subprocess.run([
    'ffmpeg', '-y', '-loglevel', 'error',
    '-i', '/home/z/my-project/source_video/bgm_original.m4a',
    '-ar', '22050', '-ac', '1',
    '/home/z/my-project/analysis/bgm_anal.wav'
], check=True)

import numpy as np
from scipy.io import wavfile
sr, data = wavfile.read('/home/z/my-project/analysis/bgm_anal.wav')
data = data.astype(np.float32) / 32768.0
print('采样率:', sr, '时长:', len(data)/sr, '秒')

# RMS 能量包络（50ms 窗口）
win = int(sr * 0.05)
n = len(data) // win
env = np.array([np.sqrt(np.mean(data[i*win:(i+1)*win]**2)) for i in range(n)])
times = np.arange(n) * 0.05

# 保存能量曲线（每 1 秒采样输出）
curve = []
for t in range(0, int(len(data)/sr)):
    idx = int(t / 0.05)
    if idx < len(env):
        curve.append((t, round(float(env[idx]), 4)))

with open('/home/z/my-project/analysis/bgm_energy.json', 'w') as f:
    json.dump(curve, f)

# 简易 onset 检测：能量突增点
diff = np.diff(env)
threshold = np.std(diff) * 1.2
onsets = []
last = -10
for i, d in enumerate(diff):
    if d > threshold and (i*0.05 - last) > 0.4:
        onsets.append(round(i*0.05, 2))
        last = i*0.05

with open('/home/z/my-project/analysis/bgm_onsets.json', 'w') as f:
    json.dump(onsets, f)

print('能量曲线(每5秒):')
for t in range(0, int(len(data)/sr), 5):
    idx = int(t / 0.05)
    bar = '#' * int(env[idx] * 120) if idx < len(env) else ''
    print(f"  {t:3d}s {'█' * max(1, int(env[idx]*60))} {env[idx]:.3f}")

print('\n节拍点数量:', len(onsets))
print('前 40 个节拍点:', onsets[:40])

# 估算 BPM（节拍间隔中位数）
if len(onsets) > 4:
    import statistics
    intervals = [round(b-a,2) for a,b in zip(onsets, onsets[1:]) if 0.3 < (b-a) < 1.5]
    if intervals:
        med = statistics.median(intervals)
        print(f'节拍间隔中位数: {med}s → BPM ≈ {60/med:.0f}')
