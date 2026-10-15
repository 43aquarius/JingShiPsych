#!/usr/bin/env python3
"""场景库 B v3（后半）：传染网格 / 解药（倒带+同盟防火墙）/ 四钥匙 / 结尾升华
v3 动画升级：网格预热闪烁、指针阻尼振荡、步进弹跳计数、
解药天降拖尾+冲击波、倒带时间码+拖影条、时钟跳格过冲、
逐字弹入钥匙、金句上升尘埃+呼吸缩放、大眼睛眨眼+星形反光
"""
import math, json, random
from render_lib import *
from render_lib import _put_alpha

SIM = json.load(open('/home/z/my-project/analysis/contagion_sim.json'))
FREE, ALLY_CURVE = SIM['free'], SIM['ally']
GRID = json.load(open('/home/z/my-project/analysis/infection_grid.json'))
FREE_DOTS, ALLY_DOTS = GRID['free']['dots'], GRID['ally']['dots']
ALLY_POS = tuple(GRID['ally']['ally'])           # (9, 5)

# 步进时间表（秒）
ST_FREE = [0.9 + 0.66*k for k in range(14)]      # 13 步 -> 到 9.48s
ST_ALLY = [0.9, 2.4, 4.2, 5.6, 6.8]             # 4 步
FREE_FLIPS = flip_map(FREE_DOTS, ST_FREE)
ALLY_FLIPS = flip_map(ALLY_DOTS, ST_ALLY)

# ============ ACT 4 传染 ============
def s_threshold(img, t, tl):
    """S24 阈值仪表（v3: 指针阻尼振荡+方块拖尾下落）"""
    a = beat(tl, 2.5, 0.2)
    slide_text(img, (W/2, 240), '从众，有门槛。', serif('M', 70), WHITE, tl, 0.05, 0.35, 'left')
    def press(tl_):
        lv = 0.0
        for k in range(3):
            p = seg(tl_, 0.5+k*0.55, 0.75+k*0.55)
            lv += 0.27*ease_out(p)
        return min(lv, 0.86)
    # 每次跳升后的指针抖动
    j = 0.04*(wobble(tl, 0.5, freq=8, decay=6) +
              0.7*wobble(tl, 1.05, freq=8, decay=6) +
              0.5*wobble(tl, 1.6, freq=8, decay=6))
    draw_gauge(img, W/2, 640, 240, min(0.92, press(tl)+j), a, RED,
               label='你的防线', label_font=serif('L', 40))
    for k in range(3):
        t0 = 0.5+k*0.55
        p = seg(tl, t0, t0+0.34)
        if p >= 1:
            person_idle(img, 430, 480+((k % 2)*66), 26, RED, t, k*0.8, a,
                        is_square=True, amp=2)
            spark_burst(img, 430, 480+((k % 2)*66)+30, tl, t0+0.34,
                        (255, 110, 100), n=5, speed=120, dur=0.3, alpha=0.6, seed=k)
        elif p > 0:
            yy = -60 + (480+((k % 2)*66)+60)*ease_in(p)
            for kk in (2, 1):
                pp = max(0.0, p - kk*0.08)
                yk = -60 + (480+((k % 2)*66)+60)*ease_in(pp)
                if yk < 440:
                    draw_person(img, 430, yk, 26*(1-0.08*kk), RED,
                                a*0.16*(3-kk)/3, is_square=True)
            draw_person(img, 430, yy, 26, RED, a, is_square=True)
    cnt = min(3, max(0, int((tl-0.5)/0.55)+1))
    draw_text_a(img, (430, 620), f'+{cnt} 附和', mono('B', 34), RED,
                a*ease_out(seg(tl, 0.5, 0.8)))
    slide_text(img, (W/2, 900), '每多一个附和者，门槛就低一截。', serif('L', 42), GRAY,
               tl, 1.9, 0.4, 'up')
    return {'shake': [(0.52+k*0.55, 0.1, 5) for k in range(3)]}

def s_grid_free(img, t, tl):
    """S25 传染网格大戏（v3: 预热闪烁+步进弹跳计数+雪崩完成冲击）
    布局：标题 2.8s 后淡出让位，计数器被「雪崩完成」接管"""
    dur = 11.6
    a = beat(tl, dur, 0.25)
    slide_text(img, (W/2, 152), '第1个附和者出现后——', serif('M', 58), WHITE, tl, 0.05, 0.4,
               'left', alpha=a*(1 - seg(tl, 2.7, 3.3)))
    draw_grid(img, tl, FREE_FLIPS, RED, preflash=0.18)
    step = min(13, max(0, int((tl-ST_FREE[0])/0.66)+1)) if tl >= ST_FREE[0] else 0
    last_t = ST_FREE[step-1] if step > 0 else None
    step_counter(img, (W-96, 54), f'STEP {step:02d} / 13', tl, last_t,
                 mono('B', 34), GRAY, a)
    frac = interp_curve(tl, ST_FREE, FREE)
    if tl < 9.85:
        count_text(img, (W/2, 218), frac*100, tl, ST_FREE[0], ST_FREE[-1]-ST_FREE[0]+0.6,
                   mono('B', 54), RED, a*0.95, glow=RED_DK, decimals=1, suffix='%')
    if tl < ST_FREE[0]+0.3:
        draw_text_a(img, (grid_pos(2, 4)[0], grid_pos(2, 4)[1]-40), '第 1 个',
                    mono('B', 26), RED, a*ease_out(seg(tl, 0.4, 0.8)))
    pop_text(img, (W/2, 218), '雪崩完成。', serif('BK', 92), RED, tl, 9.9, 0.5, glow=RED)
    speed_lines(img, W/2, 560, tl, 9.9, 0.4, RED, n=18, alpha=0.2, r0=300, r1=680, seed=25)
    impact_rings(img, W/2, 560, tl, 9.9, RED, n=2, r1=430, alpha=110)
    draw_cite(img, 'GRANOVETTER (1978) 阈值模型 · 500 人真实模拟，每一帧都是计算出来的',
              a*ease_out(seg(tl, 10.3, 10.8)))
    return {'flash': [(9.5, 0.3, RED, 0.3)], 'punch': (9.9, 0.55, 1.07)}

def s_13steps(img, t, tl):
    """S26 定格总结（v3: 逐字弹入+冲击环+背景呼吸）"""
    a = beat(tl, 2.4, 0.25)
    draw_grid(img, 999, FREE_FLIPS, RED, grid_alpha=0.28+0.05*math.sin(t*1.8), ring=False)
    char_pop(img, (W/2, H/2-110), '13步，', serif('BK', 130), WHITE, tl, 0.1, 0.13, 0.4, a)
    char_pop(img, (W/2, H/2+120), '75%陷落。', serif('BK', 130), RED, tl, 0.35, 0.13, 0.45,
             a, glow=RED)
    impact_rings(img, W/2, H/2+120, tl, 0.5, RED, n=2, r1=380, alpha=100)
    speed_lines(img, W/2, H/2, tl, 0.35, 0.38, RED, n=16, alpha=0.16, r0=330, r1=720, seed=26)
    return {'punch': (0.1, 0.45, 1.05), 'shake': [(0.35, 0.2, 8)]}

# ============ ACT 5 解药 ============
def s_pause(img, t, tl):
    a = beat(tl, 2.2, 0.2)
    slide_text(img, (W/2, 470), '怎么，按下暂停键？', serif('M', 92), WHITE, tl, 0.05, 0.45)
    draw_cite(img, 'ASCH (1956) · ALLEN & LEVINE (1971)', a*ease_out(seg(tl, 1.3, 1.7)))
    return {'zoom': (0, 2.2, 1.0, 1.03)}

def s_oneperson(img, t, tl):
    """S28 解药 = 一个人（v3: 天降+拖尾+冲击波+旋转光环）"""
    a = beat(tl, 2.8, 0.2)
    slide_text(img, (W/2-160, 430), '解药，只需要', serif('M', 84), WHITE, tl, 0.05, 0.4, 'left')
    d = ImageDraw.Draw(img)
    px, py = W/2+330, 430
    p = ease_in(seg(tl, 0.5, 1.15))
    if p >= 0.999:
        # 落地冲击波
        impact_rings(img, px, py, tl, 1.15, GOLD, n=2, r1=250, alpha=150)
        spark_burst(img, px, py, tl, 1.15, GOLD, n=14, speed=260, dur=0.55,
                    alpha=0.85, seed=28)
        # 呼吸光环 + 旋转射线
        hb = breath(t, 1.3, 0.93, 1.07)
        pr = 78*hb
        d.ellipse([px-pr, py-pr, px+pr, py+pr], outline=GOLD+(int(130*a),), width=3)
        for k in range(8):
            ang = t*0.8 + k*2*math.pi/8
            x1 = px + (96+8*math.sin(t*3+k))*math.cos(ang)
            y1 = py + (96+8*math.sin(t*3+k))*math.sin(ang)
            d.line([px+84*math.cos(ang), py+84*math.sin(ang), x1, y1],
                   fill=GOLD+(int(110*a),), width=3)
        person_idle(img, px, py, 46, GOLD, t, 0.5, a, is_square=False, amp=3)
    elif p > 0:
        yy = -70 + (py+70)*p
        for kk in (3, 2, 1):
            pp = max(0.0, p - kk*0.07)
            yk = -70 + (py+70)*pp
            if yk < py-20:
                draw_person(img, px, yk, 46*(1-0.06*kk), GOLD,
                            a*0.18*(4-kk)/4, is_square=False)
        draw_person(img, px, yy, 46, GOLD, a, is_square=False)
    pop_text(img, (W/2+330, 620), '一个人', serif('BK', 92), GOLD_HI, tl, 0.85, 0.45,
             glow=GOLD)
    return {'flash': [(1.15, 0.25, GOLD, 0.2)], 'shake': [(1.15, 0.16, 5)]}

def s_rewind(img, t, tl):
    """S29 倒带（v3: 时间码回滚+横向拖影条）"""
    a = beat(tl, 2.2, 0.2)
    T_MAX = ST_FREE[-1] + 0.3
    te = T_MAX - tl*(T_MAX/1.35)
    draw_grid(img, te, FREE_FLIPS, BLUE, ring=False, preflash=0)
    scanlines(img, tl, 14)
    d = ImageDraw.Draw(img)
    # 倒带时间码
    mm = int(te)//60
    ss = int(te) % 60
    ff = int((te % 1)*30)
    draw_text_top_a(img, (W-96, 88), f'T-{mm:02d}:{ss:02d}:{ff:02d}',
                    mono('B', 38), BLUE, a, anchor_center=False)
    # 横向拖影条
    rnd = random.Random(4)
    for k in range(6):
        ph = ((tl*2.4 + k*0.31) % 1.0)
        y = 150 + k*160 + rnd.randint(-18, 18)
        ln = 120 + int(380*(1-ph))
        x0 = int(W - (W+500)*ph)
        d.line([x0, y, x0+ln, y], fill=(140, 180, 255, int(30*(1-ph))), width=3)
    if int(tl*3) % 2 == 0:
        draw_text_top_a(img, (96, 92), '◀◀  REWIND', mono('B', 40), BLUE, a,
                        anchor_center=False)
    slide_text(img, (W/2, 180), '把时间，倒回去——', serif('M', 72), WHITE, tl, 0.1, 0.4, 'left')
    return None

def s_allydrop(img, t, tl):
    """S30 放进一个说真话的人（v3: 拖尾火花+落地冲击波）"""
    a = beat(tl, 2.8, 0.2)
    draw_grid(img, tl, {}, RED, grid_alpha=0.5, ring=False, preflash=0)
    slide_text(img, (W/2, 180), '这一次，放进一个说真话的人。', serif('M', 62), WHITE,
               tl, 0.05, 0.4)
    ax, ay = grid_pos(*ALLY_POS)
    d = ImageDraw.Draw(img)
    p = ease_in(seg(tl, 0.6, 1.3))
    if p >= 0.999:
        impact_rings(img, ax, ay, tl, 1.3, GOLD, n=2, r1=200, alpha=150)
        spark_burst(img, ax, ay, tl, 1.3, GOLD, n=16, speed=240, dur=0.6,
                    alpha=0.9, seed=30)
        ph = ((tl-1.3)*1.1) % 1.0
        rr = 20 + ph*110
        ra = int(170*(1-ph)*a)
        if ra > 0:
            d.ellipse([ax-rr, ay-rr, ax+rr, ay+rr], outline=GOLD+(ra,), width=4)
        person_idle(img, ax, ay, 15, GOLD_HI, t, 0.3, a, amp=1.5)
        pop_text(img, (ax, ay-44), '真话', mono('B', 26), GOLD, tl, 1.35, 0.3)
    else:
        drop_y = -80 + (ay+80)*p
        for kk in (3, 2, 1):
            pp = max(0.0, p - kk*0.06)
            yk = -80 + (ay+80)*pp
            if yk < ay-14:
                draw_person(img, ax, yk, 15*(1-0.07*kk), GOLD,
                            a*0.2*(4-kk)/4)
        draw_person(img, ax, drop_y, 15*(0.5+0.5*p), GOLD, a)
    return {'shake': [(1.3, 0.18, 6)]}

def s_grid_ally(img, t, tl):
    """S31 同盟防火墙（v3: 双层护罩+金点心跳+步进弹跳+封顶冲击）
    布局：标题 2.8s 后淡出让位，计数器被「封顶锤」接管"""
    dur = 7.4
    a = beat(tl, dur, 0.25)
    slide_text(img, (W/2, 152), '同一个雪崩，重放——', serif('M', 58), WHITE, tl, 0.05, 0.4,
               'left', alpha=a*(1 - seg(tl, 2.7, 3.3)))
    draw_grid(img, tl, ALLY_FLIPS, RED, preflash=0.18)
    ax, ay = grid_pos(*ALLY_POS)
    d = ImageDraw.Draw(img)
    # 金点心跳
    hb = 1 + 0.18*max(0.0, math.sin(t*3.0))**4
    draw_person(img, ax, ay, 15*hb, GOLD_HI, a)
    # 双层虚线防护圈（反向旋转）
    R = 158
    base = t*0.9
    for k in range(10):
        a0 = math.degrees(base + k*2*math.pi/10)
        a1 = a0 + 14
        d.arc([ax-R, ay-R, ax+R, ay+R], a0, a1, fill=GOLD+(int(130*a),), width=3)
    R2 = 178 + 6*math.sin(t*2.2)
    for k in range(14):
        a0 = math.degrees(-base*0.7 + k*2*math.pi/14)
        d.arc([ax-R2, ay-R2, ax+R2, ay+R2], a0, a0+9,
              fill=GOLD_DK+(int(80*a),), width=2)
    draw_text_a(img, (ax, ay-48), '真话', mono('B', 26), GOLD, a)
    step = 0
    for k in range(4):
        if tl >= ST_ALLY[k]:
            step = k+1
    last_t = ST_ALLY[step-1] if step > 0 else None
    step_counter(img, (W-96, 54), f'STEP {step:02d} / 4', tl, last_t,
                 mono('B', 34), GRAY, a)
    frac = interp_curve(tl, ST_ALLY, ALLY_CURVE)
    if tl < 5.65:
        count_text(img, (W/2, 218), frac*100, tl, ST_ALLY[0], 5.0, mono('B', 54), GOLD,
                   a*0.95, glow=GOLD_DK, decimals=1, suffix='%')
    pop_text(img, (W/2, 218), '雪崩，停在了11%。', serif('BK', 84), GOLD_HI, tl, 5.7, 0.5,
             glow=GOLD)
    impact_rings(img, W/2, 560, tl, 5.7, GOLD, n=2, r1=420, alpha=110)
    speed_lines(img, W/2, 560, tl, 5.7, 0.38, GOLD, n=18, alpha=0.18, r0=300, r1=680, seed=31)
    spark_burst(img, W/2, 220, tl, 5.7, GOLD, n=12, speed=220, dur=0.5, alpha=0.75, seed=32)
    draw_cite(img, '模拟封顶 11.4% · 现实实验里降到 5%（ALLEN & LEVINE, 1971）',
              a*ease_out(seg(tl, 6.2, 6.7)))
    return {'flash': [(5.5, 0.3, GOLD, 0.28)], 'punch': (5.7, 0.5, 1.06)}

def s_collapse(img, t, tl):
    """S32 37% → 5% 坍缩（v3: 高光带+坍缩抖动+金条火花+行进虚线）"""
    a = beat(tl, 3.2, 0.25)
    d = ImageDraw.Draw(img)
    slide_text(img, (W/2, 280), '现实实验里——', serif('L', 54), GRAY, tl, 0.05, 0.35, 'left')
    shr = ease(seg(tl, 0.7, 2.0))
    # 坍缩末端抖动
    wob = 1 + 0.05*wobble(tl, 2.0, freq=7, decay=4)
    lw = (640*(0.37*(1-shr) + 0.05*shr))*wob
    d.rounded_rectangle([300, 420, 300+max(lw, 18), 500], radius=10, fill=RED+(int(250*a),))
    _bar_shim_x(d, 300, 420, 500, lw, t, a)
    draw_text_a(img, (620, 360), '无人真话', serif('L', 42), GRAY, a)
    count_text(img, (620, 600), 37*(1-shr)+5*shr, tl, 0.7, 1.3, mono('B', 62), RED, a,
               decimals=0, suffix='%')
    gr = back(seg(tl, 1.9, 2.5))
    gw = 640*0.05*gr
    d.rounded_rectangle([980, 420, 980+max(gw, 18), 500], radius=10,
                        fill=GOLD+(int(250*a*gr),))
    if gr >= 0.99:
        # 金条呼吸光环
        hb = breath(t, 1.4, 0.93, 1.07)
        d.rounded_rectangle([980-(90*(hb-1)), 420-(90*(hb-1)), 980+max(gw, 18)+90*(hb-1),
                             500+90*(hb-1)], radius=14,
                            outline=GOLD+(int(90*a),), width=2)
        if tl >= 2.5:
            spark_burst(img, 1010, 460, tl, 2.5, GOLD, n=8, speed=150, dur=0.4,
                        alpha=0.6, seed=33)
    draw_text_a(img, (1300, 360), '1人先说真话', serif('L', 42), GOLD, a)
    count_text(img, (1300, 600), 5, tl, 1.9, 0.6, mono('B', 62), GOLD, a*gr, suffix='%')
    dash_arrow(img, (900, 460), (1020, 460), WHITE, 6, a*ease_out(seg(tl, 1.3, 1.7)),
               tl=tl, prog=ease_out(seg(tl, 1.3, 1.8)))
    slide_text(img, (W/2, 780), '一个说真话的人，抵得上整个多数派。', serif('M', 56),
               WHITE, tl, 2.3, 0.5, 'up')
    sweep_underline(img, W/2, 850, 900, tl, 2.9, GOLD_DK, 4, a*0.8)
    return {'shake': [(2.0, 0.2, 7)]}

def _bar_shim_x(d, x0, y0, y1, w, t, a):
    if w > 80:
        ph = 0.5+0.5*math.sin(t*2.6)
        bx = x0+10 + (w-64)*ph
        d.rounded_rectangle([bx, y0+7, min(bx+48, x0+w-8), y1-7], radius=5,
                            fill=(255, 170, 160, int(80*a)))

# ============ ACT 6 四把钥匙 ============
def _key_scene(img, t, tl, idx, word, color, desc, kind):
    a = beat(tl, 1.8, 0.18)
    draw_text_top_a(img, (96, 88), f'KEY 0{idx+1}', mono('B', 32), GRAY_DK, a*0.8,
                    anchor_center=False)
    # 闪烁下划线光标
    if int(tl*2.4) % 2 == 0:
        d = ImageDraw.Draw(img)
        d.rectangle([96+150, 90, 96+170, 116], fill=GRAY_DK+(int(150*a),))
    char_pop(img, (W/2, 330), word, serif('BK', 190), color, tl, 0.12, 0.14, 0.42, a,
             glow=color if color != WHITE else None)
    sweep_underline(img, W/2, 452, 420, tl, 0.5, color, 8)
    slide_text(img, (W/2, 560), desc, serif('R', 46), (205, 205, 210), tl, 0.55, 0.4, 'up')
    cy = 780
    if kind == 'write':
        d = ImageDraw.Draw(img)
        px = W/2-160 + 320*ease_out(seg(tl, 0.9, 1.5))
        d.line([W/2-160, cy, px, cy], fill=GOLD+(int(230*a),), width=10)
        d.polygon([(px, cy), (px-26, cy-22), (px-18, cy+10)], fill=GOLD+(int(230*a),))
        # 笔尖光点
        if tl >= 0.9:
            gl = breath(t, 2.2, 0.4, 1.0)
            d.ellipse([px-7*gl, cy-8*gl, px+7*gl, cy+8*gl],
                      fill=(255, 240, 200, int(160*a)))
    elif kind == 'slow':
        # 时钟跳格 + 过冲
        k = int(tl*2)
        f = seg(tl, k/2, k/2+0.16)
        extra = 1.1*math.sin(math.pi*clamp01(f))
        ang = 2*math.pi*((k+extra)/12.0)
        draw_clock(img, W/2, cy, 95, tl, a, GOLD, hand_ang=ang)
    elif kind == 'voice':
        draw_sound(img, W/2, cy, tl, a, color)
        # 小气泡弹出「真话」
        speech_bubble(img, W/2+150, cy-140, 'B', tl, 0.95, GOLD, w=104, h=84,
                      letter_size=48)
    elif kind == 'look':
        oa = ease_out(seg(tl, 0.8, 1.4)) * blink_curve(tl, 1.7, 0.2, 0.9)
        look = (math.sin(t*1.9)*0.6, 0)
        draw_eye(img, W/2, cy, 230, oa, color if color != WHITE else WHITE, GOLD, look)
    return None

def s_keys_intro(img, t, tl):
    a = beat(tl, 1.6, 0.18)
    slide_text(img, (W/2, 440), '怎么不被人群吞没——', serif('M', 74), WHITE, tl, 0.05, 0.4)
    pop_text(img, (W/2, 600), '四把钥匙。', serif('BK', 110), GOLD_HI, tl, 0.5, 0.45,
             glow=GOLD)
    impact_rings(img, W/2, 600, tl, 0.5, GOLD, n=1, r1=260, alpha=80)
    return {'punch': (0.5, 0.45, 1.05)}

def s_k_write(img, t, tl):
    return _key_scene(img, t, tl, 0, '先写', GOLD, '先写下你的答案，再看别人', 'write')

def s_k_slow(img, t, tl):
    return _key_scene(img, t, tl, 1, '慢说', WHITE, '第一个附和的，往往没过脑', 'slow')

def s_k_voice(img, t, tl):
    return _key_scene(img, t, tl, 2, '出声', RED, '你的真话，是别人的同盟', 'voice')

def s_k_look(img, t, tl):
    return _key_scene(img, t, tl, 3, '回看', CYAN, '上次沉默，是什么时候', 'look')

def s_keys_all(img, t, tl):
    """四钥匙合屏（v3: 接力发光+像素条光泽扫动）"""
    a = beat(tl, 2.8, 0.2)
    KEYS = [('先写', GOLD), ('慢说', WHITE), ('出声', RED), ('回看', CYAN)]
    d = ImageDraw.Draw(img)
    for i, (word, col) in enumerate(KEYS):
        x = W/2 + (i-1.5)*440
        d = ImageDraw.Draw(img)
        # 接力呼吸发光（各延时 0.4s）
        p = seg(tl, 0.15+i*0.2, 0.15+i*0.2+0.42)
        if p <= 0:
            continue
        ss = back(p) * breath(t-0.4*i, 1.0, 0.975, 1.025)
        lay2 = text_layer((int(W), int(120*2.4)), word, serif('BK', 120), col)
        if ss < 0.995:
            lay2 = lay2.resize((max(1, int(lay2.width*ss)), max(1, int(lay2.height*ss))),
                               Image.BILINEAR)
        _put_alpha(lay2, a)
        img.alpha_composite(lay2, (int(x-lay2.width/2), int(430-lay2.height/2)))
        n_red = [0, 2, 4, 0][i]
        cells = [GOLD_DK if (j % 5) < n_red else col for j in range(12)]
        draw_pixel_strip(img, x-170, 560, 340, 40, cells,
                        a*ease_out(seg(tl, 0.4+i*0.2, 0.7+i*0.2))*0.8, gap=6)
        # 像素条光泽扫动
        if tl >= 0.7+i*0.2:
            ph = ((tl-0.7-i*0.2)*0.5) % 1.0
            k = int(ph*12)
            if k < 12:
                xk = x-170 + k*(340+6)/12
                d.rounded_rectangle([xk, 558, min(xk+24, x+170), 602], radius=3,
                                    fill=(255, 255, 255, int(60*a)))
    slide_text(img, (W/2, 700), '四件小事，把你从人群里捞出来。', serif('L', 44), GRAY,
               tl, 1.2, 0.4, 'up')
    return {'zoom': (0, 2.8, 1.0, 1.03)}

# ============ ACT 7 结尾升华 ============
def _dot_bg(img, t, a, color):
    draw_dot_matrix(img, W/2, H/2, 560, 7, 34, a*0.8, t=t, base_color=color,
                    dot_r=4, max_alpha=90)

def s_premise(img, t, tl):
    a = beat(tl, 2.6, 0.2)
    slide_text(img, (W/2, H/2), '但这一切，有个前提——', serif('M', 84), WHITE, tl, 0.1, 0.5)
    return {'zoom': (0, 2.6, 1.0, 1.03)}

def s_in_crowd(img, t, tl):
    """站在人群里（v3: 人群各自浮动+中心呼吸）"""
    a = beat(tl, 3.6, 0.25)
    pop_text(img, (W/2, H/2-60), '你，', serif('BK', 100), WHITE, tl, 0.1, 0.4)
    pop_text(img, (W/2, H/2+80), '正站在人群里。', serif('BK', 100), GOLD_HI, tl, 0.35, 0.5,
             glow=GOLD)
    rnd = random.Random(7)
    for i in range(14):
        ang = 2*math.pi*i/14 + t*0.22
        rr = 330 + rnd.randint(-16, 16)
        x = W/2 + rr*math.cos(ang)
        y = H/2+20 + rr*math.sin(ang)*0.66
        ph = rnd.uniform(0, 6)
        draw_person(img, x, y + 5*math.sin(t*2.1+ph), 24, GRAY_DK,
                    a*ease_out(seg(tl, 0.4+i*0.05, 0.8+i*0.05)), is_square=True)
    draw_person(img, W/2, H/2+20, 30*breath(t, 1.1, 0.96, 1.04), WHITE, a)
    return {'zoom': (0, 3.6, 1.0, 1.05)}

def s_once(img, t, tl):
    """一次性场合（v3: 断开的虚线连接）"""
    a = beat(tl, 2.6, 0.2)
    slide_text(img, (W/2, 440), '一次性的场合，人容易清醒；', serif('M', 70), WHITE,
               tl, 0.05, 0.45, 'left')
    d = ImageDraw.Draw(img)
    p = ease_out(seg(tl, 0.6, 1.2))
    x1 = W/2-120-90*p
    x2 = W/2+120+90*p
    person_idle(img, x1, 680, 34, WHITE, t, 0.0, a, amp=2)
    person_idle(img, x2, 680, 34, WHITE, t, 2.1, a, amp=2)
    # 连接虚线随分离断开（渐隐）
    if p < 0.98:
        dash_arrow(img, (x1+52, 680), (x2-52, 680), GRAY_DK, 3, a*(1-p), tl=tl,
                   dash=14, gap=10, head=False)
    lay = text_layer((int(W), int(54*2.4)), '×1', mono('B', 54), GRAY_DK)
    pop_text(img, (W/2, 680), '', None, None, tl, 0.9, 0.4, a, layer=lay)
    return None

def s_daily(img, t, tl):
    """朝夕相处群体（v3: 集群呼吸+中心心跳变大）"""
    a = beat(tl, 2.6, 0.2)
    slide_text(img, (W/2, 440), '朝夕相处的群体，人容易随大流。', serif('M', 70), WHITE,
               tl, 0.05, 0.45, 'right')
    d = ImageDraw.Draw(img)
    p = ease_out(seg(tl, 0.6, 1.2))
    hb = breath(t, 1.2, 0.96, 1.04)
    for i, (dx, dy) in enumerate([(-70, -40), (70, -40), (-70, 40), (70, 40), (0, 0)]):
        x = W/2 + dx*(1.8-0.8*p)*hb
        y = 680 + dy*(1.8-0.8*p)*hb
        col = RED if i == 4 else GRAY_DK
        sz = (30 if i == 4 else 24)*hb
        if i == 4:
            continue
        draw_person(img, x, y + 3*math.sin(t*2.2+i), sz, col, a)
    hb2 = 1 + 0.22*max(0.0, math.sin(t*3.4))**4
    draw_person(img, W/2, 680, 30*hb2, RED, a)
    return None

def s_quote1(img, t, tl):
    a = beat(tl, 4.2, 0.3, 0.5)
    _dot_bg(img, t, a, GOLD)
    rising_sparks(img, t, n=18, alpha=64, color=GOLD, seed=41)
    slide_text(img, (W/2, H/2-90), '你今天的一句真话，', serif('M', 66), WHITE, tl, 0.1, 0.45, 'left')
    txt = '就是别人明天的勇气。'
    f = serif('BK', 76)
    p = seg(tl, 0.7, 1.2)
    if p > 0:
        s = back(p)*(1 + 0.01*math.sin(2*math.pi*0.7*t))
        lay = text_layer((int(W), int(f.size*2.4)), txt, f, GOLD_HI, GOLD, 18)
        if s < 0.995:
            lay = lay.resize((max(1, int(lay.width*s)), max(1, int(lay.height*s))),
                            Image.BILINEAR)
        _put_alpha(lay, a)
        img.alpha_composite(lay, (int(W/2-lay.width/2), int(H/2+70-lay.height/2)))
    return {'zoom': (0, 4.2, 1.0, 1.06)}

def s_quote2(img, t, tl):
    a = beat(tl, 4.2, 0.3, 0.5)
    _dot_bg(img, t, a, RED)
    rising_sparks(img, t, n=18, alpha=60, color=RED, seed=42)
    slide_text(img, (W/2, H/2-90), '你附和的每一个错，', serif('M', 66), WHITE, tl, 0.1, 0.45, 'left')
    txt = '都会绕一圈，回到你身上。'
    f = serif('BK', 76)
    p = seg(tl, 0.7, 1.2)
    if p > 0:
        s = back(p)*(1 + 0.01*math.sin(2*math.pi*0.7*t))
        lay = text_layer((int(W), int(f.size*2.4)), txt, f, RED, RED, 18)
        if s < 0.995:
            lay = lay.resize((max(1, int(lay.width*s)), max(1, int(lay.height*s))),
                            Image.BILINEAR)
        _put_alpha(lay, a)
        img.alpha_composite(lay, (int(W/2-lay.width/2), int(H/2+70-lay.height/2)))
    return {'zoom': (0, 4.2, 1.0, 1.06)}

def s_quote3(img, t, tl):
    a = beat(tl, 3.0, 0.3, 0.5)
    _dot_bg(img, t, a, GOLD)
    rising_sparks(img, t, n=18, alpha=64, color=GOLD, seed=43)
    pop_text(img, (W/2, H/2), '人群，会模仿你。', serif('BK', 110), GOLD_HI, tl, 0.15, 0.5,
             glow=GOLD, glow_radius=24)
    sweep_underline(img, W/2, H/2+96, 720, tl, 0.8, GOLD_DK, 5, a*0.8)
    return {'zoom': (0, 3.0, 1.0, 1.07)}

def s_next(img, t, tl):
    a = beat(tl, 2.6, 0.2)
    slide_text(img, (W/2, H/2), '所以，下次开口前——', serif('M', 80), WHITE, tl, 0.1, 0.5)
    return {'zoom': (0, 2.6, 1.0, 1.04)}

def _star_sparkle(d, x, y, r, alpha, rot=0.6):
    """四角星形反光"""
    a = int(alpha)
    if a <= 0:
        return
    for k in range(4):
        ang = rot + k*math.pi/2
        d.line([x-r*math.cos(ang), y-r*math.sin(ang),
                x+r*math.cos(ang), y+r*math.sin(ang)],
               fill=(255, 255, 255, a), width=2)

def s_eyes(img, t, tl):
    """结尾大字：你有眼睛（v3: 双眨眼+星形反光+逐字弹入+光泽扫过）"""
    a = beat(tl, 6.8, 0.4, 0.8)
    oa = ease_out(seg(tl, 0.5, 1.7)) * blink_curve(tl, 2.1, 0.22, 1.4)
    look = (math.sin(t*1.4)*0.55, math.cos(t*1.1)*0.25)
    # 眼睛光晕
    gl = breath(t, 0.8, 0.8, 1.0)
    halo = Image.new('RGBA', (620, 460), (0, 0, 0, 0))
    hd = ImageDraw.Draw(halo)
    hd.ellipse([40, 40, 580, 420], fill=GOLD+(int(24*gl*a),))
    halo = halo.filter(ImageFilter.GaussianBlur(46))
    img.alpha_composite(halo, (int(W/2-310), int(380-230)))
    draw_eye(img, W/2, 380, 340, oa, WHITE, GOLD, look)
    # 瞳孔上的星形反光（偶尔闪）
    if oa > 0.5:
        sx = W/2 + look[0]*340*0.17 - 30
        sy = 380 + look[1]*170*0.35 - 26
        st = breath(t, 0.55, 0.35, 1.0)
        _star_sparkle(ImageDraw.Draw(img), sx, sy, 16*st, 200*st*a)
    char_pop(img, (W/2, 720), '你有眼睛。', serif('BK', 150), GOLD_HI, tl, 1.5, 0.12, 0.55,
             a, glow=GOLD, glow_radius=28)
    if tl >= 2.6:
        tf = serif('BK', 150)
        lay = text_layer((int(W), int(tf.size*2.4)), '你有眼睛。', tf, GOLD_HI)
        shine_sweep(img, lay, (W/2-lay.width/2, 720-lay.height/2), tl, 2.6, 0.9, k=0.5)
    sweep_underline(img, W/2, 840, 640, tl, 2.3, GOLD, 7)
    return {'zoom': (0, 6.8, 1.0, 1.06), 'flash': [(1.5, 0.3, GOLD, 0.25)]}

def s_credits(img, t, tl):
    """数据来源快闪（v3: 行前小圆点+末行呼吸）"""
    dur = 4.4
    a = beat(tl, dur, 0.25)
    d = ImageDraw.Draw(img)
    lines = [
        ('ASCH, S. E. (1956) · PSYCHOLOGICAL MONOGRAPHS', GOLD),
        ('GRANOVETTER, M. (1978) · THRESHOLD MODELS OF COLLECTIVE BEHAVIOR', GOLD),
        ('ALLEN, V. L. & LEVINE, J. M. (1971) · SOCIAL SUPPORT AND CONFORMITY', GOLD),
        ('DEUTSCH, M. & GERARD, H. B. (1955) · A STUDY OF NORMATIVE INFLUENCE', GOLD),
    ]
    for i, (txt, col) in enumerate(lines):
        t0 = 0.3+i*0.5
        if tl >= t0:
            # 行前小圆点
            pop_text(img, (430, 380+i*110), '·', mono('B', 44), col, tl, t0, 0.25,
                     a*0.9)
            slide_text(img, (W/2+40, 380+i*110), txt, mono('R', 30), col, tl, t0, 0.4,
                       'left', 140, a*0.85)
    pop_text(img, (W/2, 900), '本片每一格数据，都来自真实模拟。', serif('L', 44),
             WHITE, tl, 2.6, 0.5, a*ease_out(seg(tl, 2.6, 3.2)))
    if tl > dur-1.0:
        k = ease((tl-(dur-1.0))/1.0)
        d.rectangle([0, 0, W, H], fill=(7, 7, 8, int(255*k)))
    return None

def s_fadeout(img, t, tl):
    """纯黑收尾"""
    return None
