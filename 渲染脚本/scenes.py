#!/usr/bin/env python3
"""场景库 A v3（前半）：冷开场 / 标题 / 阿希实验动画重演 / 数据冲击
v3 动画升级：残影下落、落地挤压+火花、速度线、冲击环、逐字弹入、
光泽扫字、待机浮动、发言浮起+声波弧、聚光灯锥、行进虚线、
心跳缩放、条形高光带、放射光线、对勾自画
每个场景 fn(img, t, tl) 返回 fx 字典（推镜/震屏/闪光）供后处理
"""
import math, json
from render_lib import *
from render_lib import _put_alpha

# ============ 线段卡（复用元件） ============
def _line_card(img, tl, a, hl=None, stagger=0.12, t0=0.1):
    """左标准线 + 右 A/B/C 三线，逐条生长；hl 高亮金色"""
    y0, y1 = 400, 800
    mid = (y0+y1)/2
    half = (y1-y0)/2
    xs = {'A': 1170, 'B': 1400, 'C': 1630}
    lens = {'A': 0.72, 'B': 1.0, 'C': 1.18}
    # 标准线
    g = ease_out(seg(tl, t0, t0+0.42))
    draw_vline(img, 420, y0, y1, 14, WHITE, a*0.95, grow=g)
    draw_text_a(img, (420, y0-64), '标准线', mono('R', 30), GRAY, a*0.9)
    for i, (k, x) in enumerate(xs.items()):
        kt = t0 + 0.25 + i*stagger
        kg = ease_out(seg(tl, kt, kt+0.3))
        L2 = (y1-y0)*lens[k]
        col, wt, aa = GRAY_DK, 11, a*0.85
        if hl == k:
            col, wt, aa = GOLD, 15, a
        draw_vline(img, x, mid-L2/2, mid+L2/2, wt, col, aa*kg, grow=1.0)
        draw_text_a(img, (x, mid-L2/2-56), k, mono('B', 52), col if hl == k else GRAY,
                    aa*max(0.25, kg))

def _scan_ruler(img, tl, a, x0=330, x1=1760, y=600, loops=2, t0=0.35):
    """测量扫描竖线：像卡尺一样左右扫过（带刻度）"""
    dur = 0.9
    for lp in range(loops):
        p = seg(tl, t0+lp*1.0, t0+lp*1.0+dur)
        if not (0 < p < 1):
            continue
        e = ease(p)
        x = x0 + (x1-x0)*e
        d = ImageDraw.Draw(img)
        aa = int(120*(1-p*0.35)*a)
        d.line([x, y-190, x, y+190], fill=CYAN+(aa,), width=2)
        for k in range(-3, 4):
            d.line([x-9, y+k*60, x+9, y+k*60], fill=CYAN+(int(aa*0.7),), width=2)
        d.ellipse([x-5, y-5, x+5, y+5], fill=CYAN+(aa,))
        break

# ============ ACT 0 冷开场：6 连切 ============
def s_cold_line(img, t, tl):
    """S01 线段题快闪（v3: 卡尺扫描线）"""
    a = beat(tl, 1.6, 0.18)
    hud_corners(img, tl, 0.5)
    draw_text_top_a(img, (96, 92), 'TEST 001 · 线段测验', mono('B', 30), GRAY, a*0.9,
                    anchor_center=False)
    _line_card(img, tl, a, stagger=0.10)
    _scan_ruler(img, tl, a, t0=0.55)
    pop_text(img, (W/2, 250), '3 秒，你就能答对。', serif('M', 84), WHITE, tl, 0.55)
    return {'zoom': (0, 1.6, 1.0, 1.03)}

def s_cold_b(img, t, tl):
    """S02 B 线金光确认（v3: 对勾自画+呼吸光环）"""
    a = beat(tl, 1.5, 0.15)
    _line_card(img, tl, a*0.75, hl='B')
    d = ImageDraw.Draw(img)
    p = seg(tl, 0.15, 0.65)
    if p > 0:
        rr = 60 + 60*ease_out(p)
        ra = int(180*(1-p)*a)
        if ra > 0:
            d.ellipse([1400-rr, 600-rr, 1400+rr, 600+rr], outline=GOLD+(ra,), width=4)
    # 落定后呼吸光环
    if tl >= 0.7:
        hb = breath(t, 1.5, 0.94, 1.06)
        rr2 = 86*hb
        d.ellipse([1400-rr2, 600-rr2, 1400+rr2, 600+rr2], outline=GOLD+(int(90*a),), width=3)
    draw_check(img, 1650, 330, tl, 0.45, 64, GOLD, 12, a*ease_out(seg(tl, 0.45, 0.6)))
    pop_text(img, (W/2, 250), 'B，和左边等长。', serif('M', 84), GOLD_HI, tl, 0.3, glow=GOLD)
    return {'flash': [(0.15, 0.22, GOLD, 0.20)]}

def s_cold_7(img, t, tl):
    """S03 7 个红方块砸落（v3: 加速下落+残影+落地挤压+火花）"""
    a = beat(tl, 1.6, 0.15)
    slide_text(img, (W/2, 420), '可前面7个人，都说——', serif('M', 80), WHITE,
               tl, 0.1, 0.4, 'left')
    for i in range(7):
        x = W/2 + (i-3)*205
        t0 = 0.35+i*0.14
        p = seg(tl, t0, t0+0.34)
        if p >= 1:
            # 落地挤压回弹
            q = seg(tl, t0+0.34, t0+0.34+0.2)
            sq = 1 + 0.26*math.sin(math.pi*clamp01(q)) if q < 1 else 1.0
            draw_person(img, x, 700, 34*sq, RED, a, is_square=True)
            spark_burst(img, x, 738, tl, t0+0.34, (255, 120, 110), n=6,
                        speed=150, dur=0.35, alpha=0.7, seed=i*3+1)
        elif p > 0:
            yy = -60 + (700+60)*ease_in(p)
            # 残影
            for k in (3, 2, 1):
                pp = max(0.0, p - k*0.09)
                yk = -60 + 760*ease_in(pp)
                if yk < 640:
                    draw_person(img, x, yk, 34*(1-0.07*k), RED,
                                a*0.15*(4-k)/4, is_square=True)
            draw_person(img, x, yy, 34, RED, a, is_square=True)
    return {'shake': [(0.42+i*0.14, 0.12, 6) for i in range(7)]}

def s_cold_wrong(img, t, tl):
    """S04 7 个气泡齐答 A → 错了（v3: 气泡浮动+速度线）"""
    a = beat(tl, 1.6, 0.15)
    for i in range(7):
        x = W/2 + (i-3)*205
        person_idle(img, x, 700, 34, RED, t, i*0.62, a, is_square=True)
        speech_bubble(img, x, 470, 'A', tl, 0.12+i*0.13)
    pop_text(img, (W/2, 240), '错了。', serif('BK', 120), RED, tl, 1.0, 0.35,
             glow=RED, glow_radius=24)
    speed_lines(img, W/2, 240, tl, 1.0, 0.32, RED, n=16, alpha=0.35, r0=170, r1=460, seed=3)
    return {'flash': [(0.98, 0.2, RED, 0.22)]}

def s_cold_37(img, t, tl):
    """S05 37% 大锤（v3: 冲击环+火花）"""
    a = beat(tl, 2.1, 0.18)
    pop_mixed(img, (W/2, 470), [('37% 的人', RED), ('，', WHITE), ('跟着说错了。', WHITE)],
              serif('M', 92), tl, 0.12, 0.5)
    count_text(img, (W/2, 700), 37, tl, 0.55, 0.9, mono('B', 64), RED, a*0.8, suffix='%')
    impact_rings(img, W/2, 700, tl, 1.45, RED, n=2, r1=180, alpha=150)
    spark_burst(img, W/2, 700, tl, 1.45, RED, n=12, speed=230, dur=0.5, alpha=0.8, seed=7)
    return {'punch': (0.12, 0.5, 1.055), 'flash': [(0.12, 0.25, RED, 0.28)],
            'shake': [(1.45, 0.18, 6)]}

def s_cold_eye(img, t, tl):
    """S06 眼睛没问题（v3: 眼睛光晕呼吸+瞳孔漫游）"""
    a = beat(tl, 1.8, 0.2)
    # 背后光晕
    gl = breath(t, 0.9, 0.75, 1.0)
    layer = Image.new('RGBA', (560, 420), (0, 0, 0, 0))
    dd = ImageDraw.Draw(layer)
    dd.ellipse([30, 30, 530, 390], fill=GOLD+(int(26*gl*a),))
    layer = layer.filter(ImageFilter.GaussianBlur(42))
    img.alpha_composite(layer, (int(W/2-280), int(380-210)))
    open_a = ease_out(seg(tl, 0.1, 0.7)) * blink_curve(tl, 2.2, 0.22, 1.9)
    look = (math.sin(t*2.1)*0.5, math.cos(t*1.7)*0.2)
    draw_eye(img, W/2, 380, 300, open_a, WHITE, GOLD, look)
    slide_text(img, (W/2, 700), '而且他们，眼睛都没问题。', serif('M', 72), WHITE,
               tl, 0.5, 0.45, 'up')
    sweep_underline(img, W/2, 800, 700, tl, 0.95, GRAY_DK, 4, a*0.8)
    return {'zoom': (0, 1.8, 1.0, 1.025)}

# ============ ACT 1 标题 ============
def s_title(img, t, tl):
    """S07 标题揭示（v3: 放射光线+逐字弹入+光泽扫过）"""
    a = beat(tl, 3.2, 0.3)
    sunburst_rays(img, W/2, 520, tl, alpha=10, n=30)
    slide_text(img, (W/2, 350), '—— 从众心理学 ——', serif('L', 42), GRAY, tl, 0.2, 0.5, 'down')
    tf = serif('BK', 195)
    char_pop(img, (W/2, 520), '三人成虎', tf, GOLD_HI, tl, 0.5, 0.14, 0.55, a,
             glow=GOLD, glow_radius=26)
    # 落定后光泽扫过
    if tl >= 1.75:
        lay = mixed_layer([('三人成虎', GOLD_HI)], tf)
        shine_sweep(img, lay, (W/2-lay.width/2, 520-lay.height/2), tl, 1.75, 0.85,
                    k=0.6)
    impact_rings(img, W/2, 520, tl, 0.5, GOLD, n=2, r1=420, alpha=70)
    sweep_underline(img, W/2, 660, 560, tl, 0.9, GOLD, 8)
    draw_text_a(img, (W/2, 760), 'CONFORMITY · SOLOMON ASCH · 1951', mono('R', 28),
                GRAY_DK, a*ease_out(seg(tl, 1.0, 1.5)))
    return {'zoom': (0, 3.2, 1.05, 1.0)}

# ============ ACT 2 阿希实验动画重演 ============
def s_1951(img, t, tl):
    """S08 年份滚动 + 人物条（v3: 数字落定冲击+扫光）"""
    a = beat(tl, 2.5, 0.2)
    count_text(img, (W/2, 380), 1951, tl, 0.1, 0.55, mono('B', 150), GOLD, a, glow=GOLD_DK)
    if tl >= 0.65:
        impact_rings(img, W/2, 380, tl, 0.65, GOLD, n=1, r1=300, alpha=90)
    draw_text_a(img, (W/2, 520), '年，斯沃斯莫尔学院。', serif('M', 66), WHITE, a)
    sweep_underline(img, W/2, 610, 700, tl, 0.5, GOLD_DK, 5, a*0.9)
    slide_text(img, (W/2, 700), '心理学家 所罗门·阿希', serif('L', 52), GRAY, tl, 0.7, 0.5, 'up')
    draw_text_a(img, (W/2, 790), 'SOLOMON E. ASCH', mono('B', 30), GOLD_DK,
                a*ease_out(seg(tl, 1.0, 1.5)))
    return {'zoom': (0, 2.5, 1.0, 1.03)}

def s_seats(img, t, tl):
    """S09 8 人入座动画（v3: 待机浮动+金圈呼吸）"""
    a = beat(tl, 3.0, 0.2)
    rec_dot(img, tl)
    slide_text(img, (W/2, 260), '房间里的8个人——', serif('M', 64), WHITE, tl, 0.1, 0.4)
    for i in range(7):
        x = W/2 - 105 + (i-3)*215
        t0 = 0.45+i*0.2
        if tl >= t0+0.38:
            person_idle(img, x, 560, 40, RED, t, i*0.73, a, is_square=True)
        else:
            draw_person_pop(img, x, 560, 40, RED, tl, t0, a,
                            is_square=True, drop_from=(-500, 0))
    # 你 + 呼吸金环
    d = ImageDraw.Draw(img)
    if tl >= 2.5:
        hb = breath(t, 1.2, 0.93, 1.07)
        pr = 74*hb
        d.ellipse([W/2+465-pr, 560-pr, W/2+465+pr, 560+pr],
                  outline=GOLD+(int(150*a),), width=3)
    draw_person_pop(img, W/2 + 465, 560, 40, GOLD, tl, 2.1, a,
                    is_square=False, label='你', label_font=serif('M', 38),
                    drop_from=(300, -260))
    if tl >= 2.5:
        person_idle(img, W/2+465, 560, 40, GOLD, t, 1.2, a, is_square=False)
    pop_text(img, (W/2, 780), '7个是演员。', serif('B', 62), RED, tl, 2.35, 0.4)
    draw_cite(img, 'ASCH, S. E. (1951). ISSUES IN THE STUDY OF CONFORMITY',
              a*ease_out(seg(tl, 2.6, 3.0)))
    return None

def s_rule(img, t, tl):
    """S10 规则 + 线自画（v3: 卡尺往返扫描）"""
    a = beat(tl, 3.0, 0.2)
    pop_text(img, (W/2, 235), '规则很简单：', serif('L', 50), GRAY, tl, 0.1, 0.35)
    slide_text(img, (W/2, 310), '哪条线，和左边一样长？', serif('M', 74), WHITE,
               tl, 0.3, 0.45, 'down')
    _line_card(img, tl, a, stagger=0.16, t0=0.5)
    _scan_ruler(img, tl, a, x0=340, x1=1740, y=600, loops=2, t0=1.3)
    return {'zoom': (0, 3.0, 1.0, 1.028)}

def s_solo(img, t, tl):
    """S11 单测 99.3%（v3: 旋转虚线外环+落定冲击环）"""
    a = beat(tl, 1.7, 0.18)
    slide_text(img, (W/2, 300), '单独作答时——', serif('L', 54), GRAY, tl, 0.05, 0.35, 'left')
    p = ease_out(seg(tl, 0.3, 1.0))
    if p > 0:
        d = ImageDraw.Draw(img)
        R = 130
        d.arc([W/2-R, 500-R, W/2+R, 500+R], -90, -90+355*0.993*p,
              fill=GOLD+(240,), width=18)
        d.arc([W/2-R, 500-R, W/2+R, 500+R], -90, 360*p, fill=GRAY_DK+(160,), width=6)
        # 旋转虚线外环
        if tl >= 0.4:
            R2 = 158
            base = t*0.7
            for k in range(12):
                a0 = math.degrees(base + k*2*math.pi/12)
                d.arc([W/2-R2, 500-R2, W/2+R2, 500+R2], a0, a0+12,
                      fill=GOLD_DK+(int(80*a),), width=3)
    count_text(img, (W/2, 500), 99.3, tl, 0.35, 0.65, mono('B', 84), GOLD_HI, a,
               glow=GOLD, decimals=1, suffix='%')
    if tl >= 1.0:
        impact_rings(img, W/2, 500, tl, 1.0, GOLD, n=1, r1=210, alpha=110)
    slide_text(img, (W/2, 740), '答对。错误率，不到1%。', serif('M', 52), WHITE,
               tl, 0.7, 0.4, 'up')
    return None

def s_critical(img, t, tl):
    """S12 关键局（v3: 文字心跳缩放）"""
    a = beat(tl, 1.8, 0.2)
    txt = '关键局，来了。'
    f = serif('BK', 110)
    p = seg(tl, 0.15, 0.57)
    if p > 0:
        s = back(p) * (1 + 0.02*math.sin(2*math.pi*2.0*max(0, tl-0.6))*ease_out(seg(tl, 0.5, 0.8)))
        lay = text_layer((int(W), int(f.size*2.4)), txt, f, WHITE,
                         (60, 60, 64), 20)
        if s < 0.995:
            lay = lay.resize((max(1, int(lay.width*s)), max(1, int(lay.height*s))),
                            Image.BILINEAR)
        _put_alpha(lay, a)
        img.alpha_composite(lay, (int(W/2-lay.width/2), int(460-lay.height/2)))
    draw_ecg(img, W/2-320, 720, 640, 120, tl, RED, speed=1.6, alpha=a*ease_out(seg(tl, 0.4, 0.8)))
    return {'punch': (0.15, 0.45, 1.045), 'flash': [(0.15, 0.18, WHITE, 0.14)]}

def s_voting(img, t, tl):
    """S13 投票大戏：7 个演员依次答 A
    v3: 发言人浮起放大+声波弧、待机浮动、气泡浮动、计数弹跳、齐错速度线"""
    dur = 4.6
    a = beat(tl, dur, 0.18)
    rec_dot(img, tl)
    draw_text_top_a(img, (96, 92), 'TRIAL 12 · CRITICAL', mono('B', 30), GRAY, a*0.9,
                    anchor_center=False)
    d = ImageDraw.Draw(img)
    mini_a = a*0.4
    draw_vline(img, 150, 150, 240, 6, WHITE, mini_a)
    for i, (k, x) in enumerate([('A', 220), ('B', 265), ('C', 310)]):
        col = GOLD if k == 'B' else GRAY_DK
        hh = {'A': 40, 'B': 84, 'C': 98}[k]
        draw_vline(img, x, 195-hh/2, 195+hh/2, 5, col, mini_a)
    for i in range(7):
        x = W/2 + (i-3)*238
        ts = 0.45+i*0.5
        act = seg(tl, ts, ts+0.22)
        lift = 12*ease_out(act)
        spoke = tl >= ts+0.22
        if spoke:
            person_idle(img, x, 660-lift, 46, (255, 110, 96), t, i*0.8, a,
                        is_square=True, amp=2.5)
        elif act > 0:
            draw_person(img, x, 660-lift, max(40*back(act), 10),
                        (238, 92, 84), a, is_square=True)
        else:
            person_idle(img, x, 660, 40, RED, t, i*0.8, a, is_square=True)
        # 座位号
        draw_text_a(img, (x, 742), f'{i+1}', mono('R', 30),
                    RED if spoke else GRAY_DK, a*0.9)
        speech_bubble(img, x, 420-lift, 'A', tl, ts)
        # 声波弧（发言瞬间）
        if ts+0.12 < tl < ts+0.8:
            for k in range(2):
                ph = ((tl-ts-0.12)*2.0 + k*0.5) % 1.0
                rr = 26 + ph*58
                aa = int(140*(1-ph)*a)
                if aa > 0:
                    d.arc([x-rr, 534-lift-rr, x+rr, 534-lift+rr], 205, 335,
                          fill=(255, 150, 140)+(aa,), width=4)
    # 进度计数（步进弹跳）
    n_spoke = min(7, max(0, int((tl-0.45)/0.5)+1))
    last_t = 0.45 + (n_spoke-1)*0.5 if n_spoke > 0 else None
    step_counter(img, (W-96, 62), f'发言 {n_spoke} / 7', tl, last_t,
                 mono('B', 34), GOLD, a)
    # 齐错揭示
    pop_text(img, (W/2, 250), '7个声音，同一个错误。', serif('B', 66), RED, tl, 3.95, 0.4,
             glow=RED)
    speed_lines(img, W/2, 660, tl, 3.95, 0.3, RED, n=14, alpha=0.28, r0=250, r1=520, seed=9)
    draw_cite(img, 'ASCH (1956) · CONFEDERATES ANSWER UNANIMOUSLY WRONG',
              a*ease_out(seg(tl, 4.0, 4.4)))
    return {'shake': [(0.47+i*0.5, 0.12, 5) for i in range(7)] +
                    [(3.95, 0.2, 6)]}

def s_yourturn(img, t, tl):
    """S14 轮到你了（v3: 聚光灯锥+人物颤抖+打字光标）"""
    a = beat(tl, 2.0, 0.2)
    spotlight_cone(img, W/2-70, 60, 660, 130, 250, tl, 0.15, 0.6, GOLD, 0.11)
    pop_text(img, (W/2-330, 400), '轮到', serif('BK', 130), WHITE, tl, 0.1, 0.4)
    pop_text(img, (W/2+40, 400), '你了', serif('BK', 130), GOLD_HI, tl, 0.25, 0.4,
             glow=GOLD, glow_radius=20)
    pop_text(img, (W/2+330, 400), '。', serif('BK', 130), WHITE, tl, 0.4, 0.3)
    # 聚光灯下的"你"（紧张颤抖）
    d = ImageDraw.Draw(img)
    pr = 70*(1+0.05*math.sin(t*5))
    ring_a = int(160*a)
    d.ellipse([W/2-70-pr, 660-pr, W/2-70+pr, 660+pr], outline=GOLD+(ring_a,), width=4)
    tr_x = 1.6*math.sin(t*26)*ease_out(seg(tl, 0.3, 0.8))
    draw_person(img, W/2-70+tr_x, 660, 42, GOLD, a, is_square=False,
                label='你', label_font=serif('M', 36))
    draw_ecg(img, W/2+180, 640, 520, 90, tl, RED, speed=2.3,
             alpha=a*ease_out(seg(tl, 0.3, 0.7)))
    # 内心独白（打字机 + 闪烁光标）
    for (xy, txt, t0) in [((W/2-320, 810), '「明明是B……」', 0.55),
                          ((W/2+60, 880), '「可他们都说A……」', 1.05)]:
        f = serif('L', 46)
        n = int((tl-t0)*14)
        if n > 0:
            lay = text_layer((int(W), int(f.size*2.4)), txt[:min(n, len(txt))], f, GRAY)
            img.alpha_composite(lay, (int(xy[0]), int(xy[1])))
            if n >= len(txt) and int(tl*2.6) % 2 == 0:
                dd = ImageDraw.Draw(img)
                dd.rectangle([xy[0]+lay.width+10, xy[1]+4, xy[0]+lay.width+30,
                              xy[1]+f.size-8], fill=GRAY+(190,))
    return {'punch': (0.1, 0.4, 1.04)}

# ============ ACT 3 数据冲击 ============
def s_rerun(img, t, tl):
    """S15 数据三连（v3: 落定冲击+底部进度线）"""
    a = beat(tl, 2.5, 0.18)
    slide_text(img, (W/2, 240), '重跑真实数据——', serif('M', 58), WHITE, tl, 0.05, 0.35)
    nums = [(123, '名被试', 0.3), (50, '组实验', 0.65), (450, '次关键判断', 1.0)]
    for i, (num, unit, t0) in enumerate(nums):
        x = W/2 + (i-1)*470
        count_text(img, (x, 470), num, tl, t0, 0.7, mono('B', 118), GOLD_HI, a, glow=GOLD_DK)
        if tl >= t0+0.7:
            impact_rings(img, x, 470, tl, t0+0.7, GOLD, n=1, r1=170, alpha=90)
        slide_text(img, (x, 620), unit, serif('L', 42), GRAY, tl, t0+0.15, 0.3, 'up')
    # 底部连接进度线
    pl = ease_out(seg(tl, 0.3, 1.7))
    d = ImageDraw.Draw(img)
    x0 = W/2-470-40
    d.line([x0, 740, x0+1000*pl, 740], fill=GOLD_DK+(int(110*a),), width=3)
    d.ellipse([x0+1000*pl-6, 734, x0+1000*pl+6, 746], fill=GOLD+(int(200*a),))
    draw_cite(img, '123 REAL PARTICIPANTS · 50 GROUPS · 12 CRITICAL TRIALS EACH',
              a*ease_out(seg(tl, 1.6, 2.0)))
    return {'zoom': (0, 2.5, 1.0, 1.03)}

def _bar_shimmer(d, x0, y0, y1, w, t, a, hi_col):
    """条形高光带往返扫动"""
    if w > 90:
        ph = 0.5+0.5*math.sin(t*2.6)
        bx = x0+12 + (w-72)*ph
        d.rounded_rectangle([bx, y0+7, min(bx+54, x0+w-8), y1-7], radius=5,
                            fill=hi_col+(int(80*a),))

def s_bar_white(img, t, tl):
    """S16 独自作答 0.7%（v3: 高光带+刻度线）"""
    a = beat(tl, 1.6, 0.18)
    slide_text(img, (W/2, 340), '独自作答，错误率——', serif('L', 54), GRAY, tl, 0.05, 0.35, 'left')
    d = ImageDraw.Draw(img)
    # 基线刻度
    d.line([370, 620, 1550, 620], fill=GRAY_DK+(int(90*a),), width=2)
    for i in range(5):
        x = 370 + 295*i
        d.line([x, 612, x, 628], fill=GRAY_DK+(int(120*a),), width=2)
    p = ease_out(seg(tl, 0.35, 0.85))
    w1 = max(16.0, 1180*0.007/0.40*p)
    d.rounded_rectangle([370, 520, 370+w1, 600], radius=10, fill=WHITE+(int(250*a),))
    _bar_shimmer(d, 370, 520, 600, w1, t, a, (255, 255, 255))
    count_text(img, (W/2, 720), 0.7, tl, 0.35, 0.5, mono('B', 76), WHITE, a,
               decimals=1, suffix='%')
    return None

def s_bar_red(img, t, tl):
    """S17 37% 红条暴涨 + ×50（v3: 高光带+端点冲击+火花）"""
    a = beat(tl, 3.4, 0.2)
    slide_text(img, (W/2, 300), '前面7人齐声报错，错误率——', serif('M', 54), WHITE,
               tl, 0.05, 0.4)
    d = ImageDraw.Draw(img)
    for i in range(9):
        x = 370 + 1180*i/8
        d.line([x, 440, x, 640], fill=GRAY_DK+(70,), width=2)
    p = ease_out(seg(tl, 0.5, 1.7))
    w2 = 1180*0.37/0.40*p
    if p > 0:
        d.rounded_rectangle([370, 470, 370+max(w2, 16), 550], radius=10,
                            fill=RED+(int(250*a),))
        if w2 > 30:
            d.rounded_rectangle([370+max(w2, 16)-46, 470, 370+max(w2, 16), 550], radius=10,
                                fill=(255, 130, 120, int(250*a)))
        _bar_shimmer(d, 370, 470, 550, w2, t, a, (255, 160, 150))
    if tl >= 1.7:
        impact_rings(img, 370+w2, 510, tl, 1.7, RED, n=2, r1=170, alpha=130)
    count_text(img, (W/2+430, 620), 37, tl, 0.5, 1.2, mono('B', 88), RED, a, glow=RED_DK,
               suffix='%')
    for i, lbl in enumerate(['0', '10', '20', '30', '40%']):
        x = 370 + 1180*i/8 if i < 4 else 1550
        draw_text_a(img, (x, 690), lbl, mono('R', 26), GRAY_DK, a*0.9)
    pop_text(img, (W/2, 790), '× 50 倍', serif('BK', 100), RED, tl, 1.9, 0.4, glow=RED)
    speed_lines(img, W/2, 790, tl, 1.9, 0.35, RED, n=16, alpha=0.3, r0=190, r1=460, seed=11)
    spark_burst(img, W/2, 790, tl, 1.9, RED, n=12, speed=250, dur=0.55, alpha=0.8, seed=13)
    draw_cite(img, 'ASCH (1956): MEAN CONFORMITY RATE 32–37% ACROSS CRITICAL TRIALS',
              a*ease_out(seg(tl, 2.4, 2.9)))
    return {'punch': (1.9, 0.5, 1.05), 'shake': [(1.9, 0.25, 9)]}

def s_50x(img, t, tl):
    """S18 暴涨 50 倍大锤（v3: 巨字呼吸+速度线）"""
    a = beat(tl, 2.4, 0.2)
    f = mono('B', 560)
    lay = text_layer((int(W), int(f.size*2.6)), '×50', f, (52, 16, 18))
    s = breath(t, 0.5, 0.985, 1.015)
    lay2 = lay.resize((max(1, int(lay.width*s)), max(1, int(lay.height*s))),
                      Image.BILINEAR)
    _put_alpha(lay2, a*0.9)
    img.alpha_composite(lay2, (int(W/2-lay2.width/2), int(H/2-lay2.height/2)))
    pop_text(img, (W/2, H/2), '错误率，暴涨50倍。', serif('BK', 96), WHITE, tl, 0.15, 0.45,
             glow=(30, 30, 33), glow_radius=16)
    speed_lines(img, W/2, H/2, tl, 0.15, 0.4, WHITE, n=22, alpha=0.22, r0=330, r1=760, seed=17)
    return {'punch': (0.15, 0.5, 1.06), 'flash': [(0.15, 0.22, WHITE, 0.2)],
            'shake': [(0.15, 0.3, 10)]}

def s_wall75(img, t, tl):
    """S19 75% 人墙（v3: 每隔3个火花+计数弹跳+末期整墙呼吸）"""
    a = beat(tl, 4.1, 0.2)
    slide_text(img, (W/2, 240), '75%的人，至少从众了一次。', serif('M', 62), WHITE,
               tl, 0.05, 0.4)
    import random as _r
    rnd = _r.Random(99)
    order = list(range(20)); rnd.shuffle(order)
    breath_all = 1 + 0.05*math.sin(t*2.0)*ease_out(seg(tl, 3.4, 3.9))
    for idx in range(20):
        r_i, c_i = divmod(idx, 5)
        x = W/2 - 2*175 + c_i*175
        y = 400 + r_i*135
        flip = 0.55 + order.index(idx)*0.185
        if tl >= flip:
            p = seg(tl, flip, flip+0.3)
            s = back(p) * (breath_all if tl > flip+0.3 else 1.0)
            rr = 30*s
            ring = 30 + 26*ease_out(p)
            d = ImageDraw.Draw(img)
            ra = int(120*(1-p)*a)
            if ra > 0:
                d.ellipse([x-ring, y-ring, x+ring, y+ring], outline=RED+(ra,), width=3)
            draw_person(img, x, y, max(rr, 8), RED, a, is_square=False)
            if order.index(idx) % 4 == 0:
                spark_burst(img, x, y, tl, flip, (255, 110, 100), n=5, speed=130,
                            dur=0.35, alpha=0.55, seed=idx)
        else:
            draw_person(img, x, y, 30, DIM_DOT, a*0.9, is_square=False)
    n_red = min(15, max(0, int((tl-0.55)/0.185)+1))
    last_t = 0.55 + (n_red-1)*0.185 if n_red > 0 else None
    step_counter(img, (W-96, H-110-26), f'从众 {n_red} / 20', tl, last_t,
                 mono('B', 36), RED, a)
    return None

def s_quarter(img, t, tl):
    """S20 只有 1/4 全程独立（v3: 金人呼吸光环+旋转虚线）"""
    a = beat(tl, 2.2, 0.2)
    d = ImageDraw.Draw(img)
    for i in range(4):
        x = W/2 + (i-1.5)*250
        t0 = 0.15 + i*0.16
        if i == 3 and tl >= t0+0.4:
            hb = breath(t, 1.1, 0.92, 1.08)
            pr = 86*hb
            d.ellipse([x-pr, 480-pr, x+pr, 480+pr], outline=GOLD+(int(140*a),), width=3)
            base = t*0.8
            R2 = 108
            for k in range(10):
                a0 = math.degrees(base + k*2*math.pi/10)
                d.arc([x-R2, 480-R2, x+R2, 480+R2], a0, a0+13,
                      fill=GOLD_DK+(int(110*a),), width=3)
            person_idle(img, x, 480, 58, GOLD, t, 0.0, a, is_square=False, amp=2.5)
        else:
            draw_person_pop(img, x, 480, 58, DIM_DOT if i == 3 else DIM_DOT, tl, t0, a,
                            is_square=False)
    pop_text(img, (W/2, 760), '全程零从众的，只有1/4。', serif('M', 66), WHITE, tl, 0.9, 0.45)
    return {'zoom': (0, 2.2, 1.0, 1.025)}

def s_why(img, t, tl):
    """S21 为什么（v3: 金句呼吸缩放+速度线）"""
    a = beat(tl, 2.2, 0.2)
    draw_text_a(img, (W/2, 430), '为什么，', serif('L', 72), GRAY, a*0.9)
    txt = '明知是错，还要跟？'
    f = serif('BK', 104)
    p = seg(tl, 0.45, 0.95)
    if p > 0:
        s = back(p)*(1 + 0.012*math.sin(2*math.pi*0.9*t))
        lay = text_layer((int(W), int(f.size*2.4)), txt, f, WHITE)
        if s < 0.995:
            lay = lay.resize((max(1, int(lay.width*s)), max(1, int(lay.height*s))),
                            Image.BILINEAR)
        _put_alpha(lay, a)
        img.alpha_composite(lay, (int(W/2-lay.width/2), int(560-lay.height/2)))
    if tl >= 0.45:
        speed_lines(img, W/2, 560, tl, 0.45, 0.3, WHITE, n=12, alpha=0.12,
                    r0=320, r1=640, seed=21)
    return None

def s_split(img, t, tl):
    """S22 分屏：信息性 vs 规范性（v3: 面板弹性滑入+行进虚线+镜片反光）"""
    dur = 5.8
    a = beat(tl, dur, 0.25)
    d = ImageDraw.Draw(img)
    pl = back(seg(tl, 0.15, 0.85))     # 左板弹性滑入
    pr = back(seg(tl, 0.35, 1.05))     # 右板弹性滑入
    lx = -462*(1-pl)
    d.rounded_rectangle([80+lx, 300, 900+lx, 900], radius=22, fill=(16, 16, 18, 245),
                        outline=GRAY_DK+(150,), width=2)
    slide_text(img, (490+lx, 380), '信息性从众', serif('B', 62), GOLD, tl, 0.4, 0.4, 'left')
    slide_text(img, (490+lx, 480), '「他们可能知道，', serif('L', 44), WHITE, tl, 0.7, 0.4, 'left')
    slide_text(img, (490+lx, 545), '我不知道的事。」', serif('L', 44), WHITE, tl, 0.85, 0.4, 'left')
    for i in range(3):
        px = 300+lx+i*180
        if tl >= 0.9+i*0.25:
            person_idle(img, px, 730, 34, RED, t, i*0.9, pl*a, is_square=True, amp=2.5)
    # 放大镜（浮动+镜片反光弧）
    if tl >= 1.5:
        scan_x = 330+lx + 300*(0.5+0.5*math.sin(t*1.6))
        my = 730 + 4*math.sin(t*1.9)
        draw_magnifier(img, scan_x, my, 62, pl*ease_out(seg(tl, 1.5, 2.0)), CYAN)
        d.arc([scan_x-62, my-62, scan_x+62, my+62], 205, 250,
              fill=(230, 250, 255, int(120*a)), width=5)
    rx = 462*(1-pr)
    d.rounded_rectangle([1020+rx, 300, 1840+rx, 900], radius=22, fill=(16, 16, 18, 245),
                        outline=GRAY_DK+(150,), width=2)
    slide_text(img, (1430+rx, 380), '规范性从众', serif('B', 62), RED, tl, 0.6, 0.4, 'right')
    slide_text(img, (1430+rx, 480), '「我不想，被当成', serif('L', 44), WHITE, tl, 0.9, 0.4, 'right')
    slide_text(img, (1430+rx, 545), '不合群的那个人。」', serif('L', 44), WHITE, tl, 1.05, 0.4, 'right')
    # 3 人围 1 人 + 行进虚线箭头
    for i, ang in enumerate([math.pi*0.85, math.pi*0.5, math.pi*0.15]):
        ax = 1430+rx + 150*math.cos(ang+0.4)
        ay = 730 - 110*math.sin(ang+0.4)
        person_idle(img, ax, ay, 26, GRAY, t, i*1.1, pr*a, is_square=True, amp=3)
        dash_arrow(img, (ax, ay), (1430+rx, 730), RED, 4,
                   pr*ease_out(seg(tl, 1.7+i*0.15, 2.0+i*0.15)) * a * 0.8,
                   tl=tl, prog=ease_out(seg(tl, 1.7+i*0.15, 2.05+i*0.15)))
    draw_person(img, 1430+rx, 730, 36, WHITE, pr*ease_out(seg(tl, 1.4, 1.8)), is_square=False)
    cl = ease_out(seg(tl, 1.0, 1.4))
    if cl > 0:
        d.line([960, 320+(-120)*(1-cl), 960, 880], fill=GRAY_DK+(int(160*cl),), width=3)
    draw_cite(img, 'DEUTSCH & GERARD (1955) · TWO FORMS OF SOCIAL INFLUENCE',
              a*ease_out(seg(tl, 4.8, 5.3)))
    return {'zoom': (0, dur, 1.0, 1.02)}

def s_virus(img, t, tl):
    """S23 传染引入（v3: 心跳双脉冲+速度线）"""
    a = beat(tl, 2.7, 0.2)
    slide_text(img, (W/2, 320), '更可怕的是——', serif('L', 60), GRAY, tl, 0.05, 0.35, 'left')
    d = ImageDraw.Draw(img)
    if tl >= 0.55:
        hb = 1 + 0.22*max(0.0, math.sin(t*3.2))**4      # 心跳式脉冲
        r = 16*hb
        d.ellipse([W/2-r, 560-r, W/2+r, 560+r], fill=RED+(int(250*a),))
        for k in range(2):
            ph = ((tl-0.55)*0.9 + k*0.5) % 1.0
            rr = 26 + ph*130
            ra = int(170*(1-ph)*a)
            if ra > 0:
                d.ellipse([W/2-rr, 560-rr, W/2+rr, 560+rr], outline=RED+(ra,), width=4)
    else:
        d.ellipse([W/2-16, 560-16, W/2+16, 560+16], fill=DIM_DOT+(int(200*a),))
    pop_text(img, (W/2, 780), '错误，会传染。', serif('BK', 100), RED, tl, 0.9, 0.45, glow=RED)
    speed_lines(img, W/2, 780, tl, 0.9, 0.32, RED, n=14, alpha=0.22, r0=200, r1=520, seed=23)
    return {'punch': (0.55, 0.4, 1.04)}
