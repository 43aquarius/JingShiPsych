#!/usr/bin/env python3
"""主渲染器 v2：49 场景时间轴 + 全局后FX + 环境动效
用法:
  python3 render_video.py --preview   # 每场景中点 + 关键时刻采样质检
  python3 render_video.py --full     # 全片渲染 ~4410 帧
  python3 render_video.py --scene N t # 单场景调试（场景序号、秒）
"""
import os, sys, time
from PIL import Image
from render_lib import W, H, FPS, BG, apply_fx, vignette, bg_particles, bg_gridlines
import scenes as A
import scenes2 as B

# (t0, t1, fn) —— 平均镜头 3.0s，硬切为主
TIMELINE = [
    # ACT 0 冷开场：6 连切
    (0.0,   1.6,   A.s_cold_line),
    (1.6,   3.1,   A.s_cold_b),
    (3.1,   4.7,   A.s_cold_7),
    (4.7,   6.3,   A.s_cold_wrong),
    (6.3,   8.4,   A.s_cold_37),
    (8.4,   10.2,  A.s_cold_eye),
    # ACT 1 标题
    (10.2,  13.4,  A.s_title),
    # ACT 2 阿希实验动画重演
    (13.4,  15.9,  A.s_1951),
    (15.9,  18.9,  A.s_seats),
    (18.9,  21.9,  A.s_rule),
    (21.9,  23.6,  A.s_solo),
    (23.6,  25.4,  A.s_critical),
    (25.4,  30.0,  A.s_voting),      # 投票大戏
    (30.0,  32.0,  A.s_yourturn),
    # ACT 3 数据冲击
    (32.0,  34.5,  A.s_rerun),
    (34.5,  36.1,  A.s_bar_white),
    (36.1,  39.5,  A.s_bar_red),
    (39.5,  41.9,  A.s_50x),
    (41.9,  46.0,  A.s_wall75),
    (46.0,  48.2,  A.s_quarter),
    (48.2,  50.4,  A.s_why),
    (50.4,  56.2,  A.s_split),      # 信息性 vs 规范性
    (56.2,  58.9,  A.s_virus),
    # ACT 4 传染
    (58.9,  61.4,  B.s_threshold),
    (61.4,  73.0,  B.s_grid_free),   # 网格雪崩大戏
    (73.0,  75.4,  B.s_13steps),
    # ACT 5 解药
    (75.4,  77.6,  B.s_pause),
    (77.6,  79.8,  B.s_oneperson),
    (79.8,  82.0,  B.s_rewind),
    (82.0,  84.8,  B.s_allydrop),
    (84.8,  92.2,  B.s_grid_ally),   # 同盟防火墙
    (92.2,  95.4,  B.s_collapse),
    # ACT 6 四钥匙
    (95.4,  97.0,  B.s_keys_intro),
    (97.0,  98.8,  B.s_k_write),
    (98.8,  100.6, B.s_k_slow),
    (100.6, 102.4, B.s_k_voice),
    (102.4, 104.2, B.s_k_look),
    (104.2, 107.0, B.s_keys_all),
    # ACT 7 结尾升华
    (107.0, 109.6, B.s_premise),
    (109.6, 113.2, B.s_in_crowd),
    (113.2, 115.8, B.s_once),
    (115.8, 118.4, B.s_daily),
    (118.4, 122.6, B.s_quote1),
    (122.6, 126.8, B.s_quote2),
    (126.8, 129.8, B.s_quote3),
    (129.8, 132.4, B.s_next),
    (132.4, 139.2, B.s_eyes),       # 你有眼睛（BGM 高潮）
    (139.2, 143.6, B.s_credits),
    (143.6, 147.0, B.s_fadeout),
]
DURATION = TIMELINE[-1][1]
TOTAL_FRAMES = int(DURATION*FPS)

OUT_DIR = '/home/z/my-project/render/frames'
os.makedirs(OUT_DIR, exist_ok=True)

def render_frame(t):
    img = Image.new('RGBA', (W, H), BG+(255,))
    bg_gridlines(img, t)
    bg_particles(img, t)
    fx = None
    for t0, t1, fn in TIMELINE:
        if t0 <= t < t1:
            fx = fn(img, t, t-t0)
            break
    if fx:
        img = apply_fx(img, t - _cur_t0(t), fx)
    vignette(img)
    return img.convert('RGB')

def _cur_t0(t):
    for t0, t1, fn in TIMELINE:
        if t0 <= t < t1:
            return t0
    return 0.0

def encode_full():
    """v3：边渲染边编码，帧直接管道喂给 ffmpeg（免 PNG 落盘）"""
    import subprocess
    OUT = '/home/z/my-project/render/video_v3.mp4'
    cmd = ['ffmpeg', '-y', '-loglevel', 'error',
           '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
           '-i', '-',
           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20',
           '-pix_fmt', 'yuv420p', OUT]
    log = open('/home/z/my-project/render/encode_v3.log', 'w')
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=log, stderr=log)
    t0 = time.time()
    for i in range(TOTAL_FRAMES):
        img = render_frame(i/FPS)
        proc.stdin.write(img.tobytes())
        if i % 300 == 0:
            print(f'{i}/{TOTAL_FRAMES} ({i/TOTAL_FRAMES*100:.0f}%) '
                  f'{i/max(0.001, time.time()-t0):.1f}fps', flush=True)
    proc.stdin.close()
    proc.wait()
    print(f'编码完成 {OUT} 耗时 {(time.time()-t0)/60:.1f} 分钟')


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else '--preview'
    if mode == '--encode':
        encode_full()
    elif mode == '--preview':
        ts = sorted(set([round((t0+t1)/2, 2) for t0, t1, _ in TIMELINE]) |
                    {2.5, 4.9, 6.8, 27.5, 28.3, 29.3, 31.4, 64.0, 67.0, 70.0, 72.0,
                     80.8, 83.5, 89.5, 91.5, 93.8, 98.0, 101.5, 133.5, 136.0, 140.0})
        os.makedirs('/home/z/my-project/render/preview2', exist_ok=True)
        for t in ts:
            t0 = time.time()
            img = render_frame(t)
            fn_used = [f.__name__ for a, b, f in TIMELINE if a <= t < b]
            img.save(f'/home/z/my-project/render/preview2/f_{t:07.2f}.png')
            print(f't={t:6.2f}s {fn_used} 耗时{(time.time()-t0)*1000:.0f}ms')
        print('预览帧已保存到 render/preview2/')
    elif mode == '--scene':
        idx = int(sys.argv[2]); tt = float(sys.argv[3])
        t0, t1, fn = TIMELINE[idx]
        img = render_frame(t0 + tt)
        os.makedirs('/home/z/my-project/render/preview2', exist_ok=True)
        p = f'/home/z/my-project/render/preview2/scene{idx:02d}_{tt:.2f}.png'
        img.save(p)
        print('saved', p)
    else:
        start = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        end = int(sys.argv[3]) if len(sys.argv) > 3 else TOTAL_FRAMES
        for i in range(start, min(end, TOTAL_FRAMES)):
            t = i/FPS
            img = render_frame(t)
            img.save(f'{OUT_DIR}/f_{i:05d}.png')
            if i % 300 == 0:
                print(f'{i}/{TOTAL_FRAMES} ({i/TOTAL_FRAMES*100:.0f}%)', flush=True)
        print(f'帧 {start}-{min(end, TOTAL_FRAMES)} 渲染完成')

if __name__ == '__main__':
    main()
