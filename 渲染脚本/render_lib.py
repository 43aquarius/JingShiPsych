#!/usr/bin/env python3
"""渲染基础库 v3：动画工具箱
风格：仿 B 站《以牙还牙》黑金极简数据可视化动画
v2：滑入/弹入/打字机文字、语音气泡、眼睛、心电图、仪表盘、
    时钟、声波、放大镜、HUD 边框/REC、传染网格组件、
    环境粒子/网格/暗角、全局后 FX（推镜/震屏/闪光）
v3：文字图层缓存（渲染提速）、逐字弹入、速度线、冲击环、火花爆、
    光泽扫字、待机浮动、行进虚线箭头、聚光灯锥、上升尘埃、
    放射光線、对勾自画、阻尼振荡、步进弹跳计数器、眨眼曲线
"""
import math, random
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

W, H = 1920, 1080
FPS = 30

# ============ 色板 ============
BG      = (7, 7, 8)
GOLD    = (255, 194, 77)
GOLD_HI = (255, 220, 140)
GOLD_DK = (140, 105, 40)
RED     = (229, 72, 77)
RED_DK  = (120, 32, 36)
WHITE   = (244, 244, 246)
GRAY    = (136, 136, 140)
GRAY_DK = (70, 70, 74)
CYAN    = (120, 200, 215)
BLUE    = (108, 160, 255)      # 倒带用
DIM_DOT = (90, 90, 96)         # 网格基点

FONT_DIR = '/home/z/my-project/assets/fonts'
SERIF_DIR = '/usr/share/fonts/truetype/noto-serif-sc'

_font_cache = {}
_SERIF_MAP = {'XL':'ExtraLight','L':'Light','R':'Regular','M':'Medium',
              'SB':'SemiBold','B':'Bold','XB':'ExtraBold','BK':'Black'}
def serif(weight, size):
    name = _SERIF_MAP[weight]
    path = f'{SERIF_DIR}/NotoSerifSC-{name}.ttf'
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]

def mono(weight, size):
    name = {'R': 'Regular', 'L': 'Light', 'SB': 'SemiBold', 'B': 'Bold'}[weight]
    path = f'/usr/share/fonts/truetype/chinese/SarasaMonoSC-{name}.ttf'
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]

# ============ 缓动 ============
def clamp01(x): return max(0.0, min(1.0, x))
def ease(t):    # ease-in-out
    t = clamp01(t)
    return t*t*(3-2*t)
def ease_out(t):
    t = clamp01(t)
    return 1-(1-t)**3
def ease_in(t):
    t = clamp01(t)
    return t**3
def back(t, s=1.70158):
    """过冲弹簧 ease-out-back"""
    t = clamp01(t); t -= 1
    return 1 + t*t*((s+1)*t + s)
def seg(t, t0, t1):
    if t1 == t0: return 1.0
    return clamp01((t-t0)/(t1-t0))

def beat(tl, dur, fade_in=0.3, fade_out=0.0):
    """场景透明度包络（硬切风格：默认无淡出）"""
    if tl < 0: return 0
    a_in = ease_out(tl/fade_in) if fade_in > 0 else 1
    a_out = clamp01((dur-tl)/fade_out) if fade_out > 0 else 1
    return min(a_in, a_out)

# ============ 文字（基础，v3 带图层缓存） ============
@lru_cache(maxsize=4096)
def _text_layer_cached(cw, ch, text, font, fill, glow, glow_radius, glow_alpha):
    size = (cw, ch)
    tmp = Image.new('RGBA', size, (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    bbox = d.textbbox((0, 0), text, font=font)
    if glow:
        g = Image.new('RGBA', size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(g)
        gd.text((-bbox[0], -bbox[1]), text, font=font, fill=glow + (glow_alpha,))
        g = g.filter(ImageFilter.GaussianBlur(glow_radius))
        tmp.alpha_composite(g)
    d = ImageDraw.Draw(tmp)
    d.text((-bbox[0], -bbox[1]), text, font=font, fill=fill + (255,))
    bbox2 = tmp.getbbox()
    if bbox2:
        tmp = tmp.crop(bbox2)
    return tmp

def text_layer(size, text, font, fill, glow=None, glow_radius=18, glow_alpha=200):
    return _text_layer_cached(int(size[0]), int(size[1]), text, font,
                              tuple(fill), tuple(glow) if glow else None,
                              glow_radius, glow_alpha)

def _put_alpha(layer, alpha):
    if alpha >= 0.999:
        return layer
    a = layer.split()[3].point(lambda p: int(p * clamp01(alpha)))
    out = layer.copy()
    out.putalpha(a)
    return out

def draw_text_a(img, xy_center, text, font, fill, alpha=1.0, glow=None, glow_radius=18):
    if alpha <= 0: return
    layer = text_layer((int(W), int(font.size*2.4)), text, font, fill, glow, glow_radius)
    _put_alpha(layer, alpha)
    img.alpha_composite(layer, (int(xy_center[0]-layer.width/2), int(xy_center[1]-layer.height/2)))

def draw_text_top_a(img, xy, text, font, fill, alpha=1.0, glow=None, glow_radius=18,
                    anchor_center=True):
    if alpha <= 0: return
    layer = text_layer((int(W), int(font.size*2.4)), text, font, fill, glow, glow_radius)
    _put_alpha(layer, alpha)
    x = int(xy[0] - (layer.width/2 if anchor_center else 0))
    img.alpha_composite(layer, (x, int(xy[1])))

def mixed_layer(parts, font):
    """多色混排 -> 单个 RGBA 图层 parts=[(text,color),...]"""
    layers = [text_layer((int(W), int(font.size*2.6)), t, font, c) for t, c in parts]
    total_w = sum(l.width for l in layers)
    h = max(l.height for l in layers)
    comb = Image.new('RGBA', (total_w, h), (0,0,0,0))
    x = 0
    for l in layers:
        comb.alpha_composite(l, (x, (h-l.height)//2))
        x += l.width
    return comb

def draw_mixed_a(img, xy_center, parts, font, alpha=1.0):
    if alpha <= 0: return
    layer = _put_alpha(mixed_layer(parts, font), alpha)
    img.alpha_composite(layer, (int(xy_center[0]-layer.width/2), int(xy_center[1]-layer.height/2)))

# ============ 文字（动画版） ============
def pop_text(img, xy_center, text, font, fill, tl, t0=0.0, dur=0.4,
             alpha=1.0, glow=None, glow_radius=18, layer=None):
    """弹入文字：0 → 1.1 → 1 过冲缩放"""
    p = seg(tl, t0, t0+dur)
    if p <= 0 or alpha <= 0: return
    s = back(p)
    if s <= 0.03: return
    lay = layer if layer is not None else \
        text_layer((int(W), int(font.size*2.4)), text, font, fill, glow, glow_radius)
    if s < 0.995:
        lay = lay.resize((max(1, int(lay.width*s)), max(1, int(lay.height*s))), Image.BILINEAR)
    _put_alpha(lay, alpha)
    img.alpha_composite(lay, (int(xy_center[0]-lay.width/2), int(xy_center[1]-lay.height/2)))

def pop_layer(img, xy_center, lay, tl, t0, dur=0.4, alpha=1.0):
    pop_text(img, xy_center, '', None, None, tl, t0, dur, alpha, layer=lay)

def pop_mixed(img, xy_center, parts, font, tl, t0=0.0, dur=0.45, alpha=1.0):
    if alpha <= 0: return
    pop_layer(img, xy_center, mixed_layer(parts, font), tl, t0, dur, alpha)

def slide_text(img, xy_center, text, font, fill, tl, t0=0.0, dur=0.45,
               direction='left', dist=180, alpha=1.0, glow=None, glow_radius=18):
    """滑入文字：left/right/up/down"""
    p = seg(tl, t0, t0+dur)
    if p <= 0 or alpha <= 0: return
    e = ease_out(p)
    dx, dy = 0, 0
    if direction == 'left':   dx = -dist*(1-e)
    elif direction == 'right': dx = dist*(1-e)
    elif direction == 'up':   dy = dist*(1-e)
    elif direction == 'down': dy = -dist*(1-e)
    layer = text_layer((int(W), int(font.size*2.4)), text, font, fill, glow, glow_radius)
    _put_alpha(layer, alpha)
    img.alpha_composite(layer, (int(xy_center[0]+dx-layer.width/2),
                                 int(xy_center[1]+dy-layer.height/2)))

def typewriter(img, xy_left, text, font, fill, tl, t0=0.0, cps=12, alpha=1.0):
    """打字机（左锚定）"""
    n = int((tl-t0)*cps)
    if n <= 0 or alpha <= 0: return
    draw_text_top_a(img, (xy_left[0], xy_left[1]), text[:n], font, fill, alpha,
                    anchor_center=False)

def count_text(img, xy_center, target, tl, t0, dur, font, color, alpha=1.0,
               glow=None, decimals=0, suffix=''):
    """数字滚动"""
    p = ease_out(seg(tl, t0, t0+dur))
    if p <= 0 or alpha <= 0: return
    v = target * p
    if decimals > 0:
        s = f'{v:.{decimals}f}{suffix}'
    else:
        s = f'{int(round(v))}{suffix}'
    draw_text_a(img, xy_center, s, font, color, alpha, glow)

# ============ 图形元件 ============
def draw_pixel_strip(img, x, y, w, h, cells, alpha=1.0, gap=4, radius=2):
    if alpha <= 0: return
    n = len(cells)
    cw = (w - gap*(n-1)) / n
    layer = Image.new('RGBA', (int(w)+4, int(h)+4), (0,0,0,0))
    d = ImageDraw.Draw(layer)
    for i, c in enumerate(cells):
        if c is None: continue
        cx = i*(cw+gap)
        d.rounded_rectangle([cx, 0, cx+cw, h], radius=radius, fill=c+(int(255*clamp01(alpha)),))
    img.alpha_composite(layer, (int(x), int(y)-2))

def draw_dot_matrix(img, cx, cy, R, rows, cols, alpha=1.0, t=0.0, dot_r=5,
                    base_color=GOLD, phase=0.0, max_alpha=90):
    """圆环点阵（金句背景）"""
    if alpha <= 0: return
    layer = Image.new('RGBA', (int(2*R)+20, int(2*R)+20), (0,0,0,0))
    d = ImageDraw.Draw(layer)
    cx0, cy0 = R+10, R+10
    rnd = random.Random(42)
    for ri in range(1, rows+1):
        r = R * ri / rows
        n = max(6, int(cols * ri / rows))
        for ci in range(n):
            ang = 2*math.pi*ci/n + phase + ri*0.05 + t*0.12*ri/rows
            x = cx0 + r*math.cos(ang)
            y = cy0 + r*math.sin(ang)
            jit = (rnd.random()-0.5)*3
            wave = 0.5 + 0.5*math.sin(2*math.pi*((r - t*260) / 300))
            a = int(max_alpha * (0.4 + 0.6*wave) * clamp01(alpha))
            d.ellipse([x-dot_r+jit, y-dot_r, x+dot_r, y+dot_r], fill=base_color+(a,))
    img.alpha_composite(layer, (int(cx-R-10), int(cy-R-10)))

def draw_person(img, x, y, size, color, alpha=1.0, is_square=False,
                label=None, label_font=None, label_color=WHITE):
    if alpha <= 0: return
    size = max(2, int(size))
    layer = Image.new('RGBA', (size*3+4, size*3+4), (0,0,0,0))
    d = ImageDraw.Draw(layer)
    cx, cy = size*1.5, size*1.5
    a = int(255*clamp01(alpha))
    if is_square:
        d.rounded_rectangle([cx-size, cy-size, cx+size, cy+size], radius=6, fill=color+(a,))
    else:
        d.ellipse([cx-size, cy-size, cx+size, cy+size], fill=color+(a,))
    if label and label_font:
        d.text((cx-size*1.1, cy+size*1.35), label, font=label_font, fill=label_color+(a,))
    img.alpha_composite(layer, (int(x-size*1.5), int(y-size*1.5)))

def draw_person_pop(img, x, y, size, color, tl, t0, alpha=1.0, is_square=False,
                    label=None, label_font=None, drop_from=None):
    """弹入/落入人形，drop_from=(dx,dy) 起始偏移"""
    p = seg(tl, t0, t0+0.38)
    if p <= 0: return
    s = back(p)
    sz = max(2, size*s)
    ox, oy = 0, 0
    if drop_from is not None:
        ox, oy = drop_from[0]*(1-ease_out(p)), drop_from[1]*(1-ease_out(p))
    draw_person(img, x+ox, y+oy, sz, color, alpha, is_square, label, label_font)

def draw_vline(img, x, y0, y1, width, color, alpha=1.0, grow=1.0):
    """实验线段：grow 从中心向两端生长 0..1"""
    if alpha <= 0 or grow <= 0: return
    mid = (y0+y1)/2
    half = (y1-y0)/2*clamp01(grow)
    d = ImageDraw.Draw(img)
    a = int(255*clamp01(alpha))
    d.line([x, mid-half, x, mid+half], fill=color+(a,), width=width)
    d.ellipse([x-width/2, mid-half-width/2, x+width/2, mid-half+width/2], fill=color+(a,))
    d.ellipse([x-width/2, mid+half-width/2, x+width/2, mid+half+width/2], fill=color+(a,))

def draw_cite(img, text, alpha=1.0, y=None, color=GRAY_DK):
    if alpha <= 0: return
    f = serif('L', 26)
    if y is None: y = H - 58
    draw_text_a(img, (W/2, y), text, f, color, alpha)

def speech_bubble(img, cx, top_y, letter, tl, t0, color=RED, w=132, h=104,
                  letter_col=WHITE, letter_size=64, float_after=True):
    """语音气泡弹入（含下尾巴）；落定后轻微浮动"""
    p = seg(tl, t0, t0+0.34)
    if p <= 0: return
    s = back(p)
    if s <= 0.05: return
    dy = 3.5 * math.sin((tl - t0) * 2.4) if (float_after and p >= 1) else 0
    top_y = top_y + dy
    w2, h2 = int(w*s), int(h*s)
    tail = int(30*s)
    layer = Image.new('RGBA', (w2+12, h2+tail+12), (0,0,0,0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([4, 4, w2+4, h2+4], radius=16, fill=color+(238,))
    d.polygon([(w2/2-12, h2), (w2/2+12, h2), (w2/2+2, h2+tail)], fill=color+(238,))
    if p >= 0.3:
        fs = mono('B', max(12, int(letter_size*clamp01((p-0.3)/0.35))))
        d.text(((w2+8-fs.size)/2, (h2-fs.size)/2 - 2), letter, font=fs,
               fill=letter_col+(255,))
    img.alpha_composite(layer, (int(cx-layer.width/2), int(top_y)))

def draw_eye(img, cx, cy, w, open_a=1.0, color=WHITE, pupil=GOLD, look=(0.0, 0.0)):
    """眼睛：open_a 睁眼度 0..1，look 瞳孔偏移 -1..1"""
    h = w*0.5*clamp01(open_a)
    if h < 2: return
    layer = Image.new('RGBA', (int(w)+90, int(w)+90), (0,0,0,0))
    d = ImageDraw.Draw(layer)
    c, m = layer.width/2, layer.height/2
    d.ellipse([c-w/2, m-h, c+w/2, m+h], outline=color+(235,), width=9)
    pr = w*0.17
    px = c + look[0]*w*0.17
    py = m + look[1]*h*0.35
    d.ellipse([px-pr, py-pr, px+pr, py+pr], fill=pupil+(255,))
    hr = pr*0.28
    d.ellipse([px-pr*0.55-hr, py-pr*0.55-hr, px-pr*0.55+hr, py-pr*0.55+hr],
              fill=(255,255,255,230,))
    img.alpha_composite(layer, (int(cx-layer.width/2), int(cy-layer.height/2)))

def draw_ecg(img, x, y, w, h, tl, color=RED, speed=0.8, alpha=1.0, lw=5):
    """心电图：滚动波形 + 移动亮点"""
    if alpha <= 0: return
    d = ImageDraw.Draw(img)
    beat_pts = [0.0, 0.0, 0.12, -0.06, 0.18, 0.18, 0.22, -0.42, 0.26, 1.0,
                0.30, -0.55, 0.36, 0.14, 0.48, 0.0, 0.62, 0.0, 1.0, 0.0]
    period = 1.0
    n = 220
    pts = []
    for i in range(n+1):
        u = i/n
        tt = (u*4*period + tl*speed) % period
        k = int(tt/period*len(beat_pts))
        k2 = min(k+1, len(beat_pts)-1)
        f = tt/period*len(beat_pts) - k
        v = beat_pts[k] + (beat_pts[k2]-beat_pts[k])*f
        pts.append((x+u*w, y - v*h*0.42))
    a = int(230*clamp01(alpha))
    d.line(pts, fill=color+(a,), width=lw, joint='curve')
    # 亮点
    ph = (tl*speed) % period / period
    li = int(ph*4*n) % (len(pts)-1)
    px, py = pts[li]
    d.ellipse([px-9, py-9, px+9, py+9], fill=color+(int(255*clamp01(alpha)),))

def draw_gauge(img, cx, cy, R, frac, alpha=1.0, color=GOLD, label=None,
               label_font=None, needle_from=None):
    """半圆仪表盘：frac 0(左)→1(右) 指针"""
    if alpha <= 0: return
    d = ImageDraw.Draw(img)
    a = int(255*clamp01(alpha))
    d.arc([cx-R, cy-R, cx+R, cy+R], 180, 360, fill=GRAY_DK+(int(a*0.9),), width=9)
    for k in range(5):
        ang = math.pi + math.pi*k/4
        x1 = cx + (R-26)*math.cos(ang); y1 = cy + (R-26)*math.sin(ang)
        x2 = cx + (R-8)*math.cos(ang);  y2 = cy + (R-8)*math.sin(ang)
        d.line([x1, y1, x2, y2], fill=GRAY+(a,), width=4)
    f = clamp01(frac) if needle_from is None else needle_from + (frac-needle_from)
    f = clamp01(f)
    ang = math.pi + math.pi*f
    nx = cx + (R*0.78)*math.cos(ang); ny = cy + (R*0.78)*math.sin(ang)
    d.line([cx, cy, nx, ny], fill=color+(a,), width=8)
    d.ellipse([cx-13, cy-13, cx+13, cy+13], fill=color+(a,))
    if label and label_font:
        draw_text_a(img, (cx, cy+R*0.36), label, label_font, GRAY, alpha)

def draw_clock(img, cx, cy, R, tl, alpha=1.0, color=GOLD, hand_speed=2.4,
               hand_ang=None):
    if alpha <= 0: return
    d = ImageDraw.Draw(img)
    a = int(255*clamp01(alpha))
    d.ellipse([cx-R, cy-R, cx+R, cy+R], outline=color+(a,), width=8)
    for k in range(12):
        ang = 2*math.pi*k/12
        x1 = cx+(R-16)*math.sin(ang); y1 = cy-(R-16)*math.cos(ang)
        x2 = cx+(R-6)*math.sin(ang);  y2 = cy-(R-6)*math.cos(ang)
        d.line([x1, y1, x2, y2], fill=color+(int(a*0.6),), width=4)
    if hand_ang is not None:
        ang = hand_ang
    else:
        ang = 2*math.pi*(tl*hand_speed/12.0)
    hx = cx + R*0.62*math.sin(ang); hy = cy - R*0.62*math.cos(ang)
    d.line([cx, cy, hx, hy], fill=WHITE+(a,), width=8)
    d.ellipse([cx-9, cy-9, cx+9, cy+9], fill=WHITE+(a,))

def draw_sound(img, cx, cy, tl, alpha=1.0, color=GOLD):
    """声波：中心点 + 三圈扩散弧"""
    if alpha <= 0: return
    d = ImageDraw.Draw(img)
    a = int(255*clamp01(alpha))
    d.ellipse([cx-14, cy-14, cx+14, cy+14], fill=color+(a,))
    for k in range(3):
        ph = (tl*1.1 + k/3.0) % 1.0
        r = 34 + ph*110
        aa = int(220*(1-ph)*clamp01(alpha))
        if aa > 0:
            d.arc([cx-r, cy-r, cx+r, cy+r], -52, 52, fill=color+(aa,), width=7)
            d.arc([cx-r, cy-r, cx+r, cy+r], 128, 232, fill=color+(aa,), width=7)

def draw_magnifier(img, cx, cy, R, alpha=1.0, color=CYAN, slide=0.0):
    if alpha <= 0: return
    d = ImageDraw.Draw(img)
    a = int(255*clamp01(alpha))
    d.ellipse([cx-R, cy-R, cx+R, cy+R], outline=color+(a,), width=10)
    hx = cx + R*0.8; hy = cy + R*0.8
    d.line([hx, hy, hx+R*0.85, hy+R*0.85], fill=color+(a,), width=14)

def draw_arrow(img, p0, p1, color, width=7, alpha=1.0, prog=1.0):
    """箭头带生长动画"""
    if alpha <= 0 or prog <= 0: return
    d = ImageDraw.Draw(img)
    a = int(255*clamp01(alpha))
    x0, y0 = p0
    x1 = x0 + (p1[0]-x0)*clamp01(prog)
    y1 = y0 + (p1[1]-y0)*clamp01(prog)
    d.line([x0, y0, x1, y1], fill=color+(a,), width=width)
    ang = math.atan2(p1[1]-y0, p1[0]-x0)
    Lh = 20
    a1 = ang + math.radians(153); a2 = ang - math.radians(153)
    if prog >= 0.999:
        d.polygon([(x1, y1), (x1+Lh*math.cos(a1), y1+Lh*math.sin(a1)),
                   (x1+Lh*math.cos(a2), y1+Lh*math.sin(a2))], fill=color+(a,))

def sweep_underline(img, cx, y, w, tl, t0, color=GOLD, width=7, alpha=1.0):
    p = ease_out(seg(tl, t0, t0+0.5))
    if p <= 0 or alpha <= 0: return
    d = ImageDraw.Draw(img)
    d.line([cx-w/2, y, cx-w/2 + w*p, y], fill=color+(int(255*clamp01(alpha)),), width=width)

def hud_corners(img, tl, alpha=0.7, m=50, arm=None, color=GRAY):
    """四角括号滑入"""
    arm = arm or int(m*1.5)
    e = ease_out(seg(tl, 0, 0.5))
    if e <= 0 or alpha <= 0: return
    d = ImageDraw.Draw(img)
    a = int(200*clamp01(alpha)*e)
    off = int(36*(1-e))
    L = int(arm*e)
    for sx, sy, hx, hy in [(m, m, 1, 1), (W-m, m, -1, 1), (m, H-m, 1, -1), (W-m, H-m, -1, -1)]:
        bx, by = sx+hx*off, sy+hy*off
        d.line([bx, by, bx+hx*L, by], fill=color+(a,), width=5)
        d.line([bx, by, bx, by+hy*L], fill=color+(a,), width=5)

def rec_dot(img, tl, alpha=0.85):
    """REC 录制指示灯（闪烁）"""
    if int(tl*1.8) % 2 != 0: return
    d = ImageDraw.Draw(img)
    a = int(225*clamp01(alpha))
    d.ellipse([W-158, 66, W-128, 96], fill=RED+(a,))
    draw_text_top_a(img, (W-112, 62), 'REC', mono('B', 34), GRAY, alpha, anchor_center=False)

# ============ 环境背景 ============
_PARTS = None
def bg_particles(img, t, alpha=15):
    global _PARTS
    if _PARTS is None:
        rnd = random.Random(11)
        _PARTS = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(5, 16),
                   rnd.uniform(12, 46), rnd.choice([GOLD, GRAY, RED]), rnd.uniform(0, 9))
                  for _ in range(30)]
    d = ImageDraw.Draw(img)
    for (x0, y0, r, spd, col, ph) in _PARTS:
        x = (x0 + t*spd) % (W+80) - 40
        y = y0 + math.sin(t*0.6 + ph)*14
        a = int(alpha*(0.45 + 0.55*math.sin(t*1.2 + ph*2)))
        if a > 0:
            d.ellipse([x-r, y-r, x+r, y+r], fill=col+(a,))

def bg_gridlines(img, t, alpha=9):
    d = ImageDraw.Draw(img)
    off = (t*16) % 144
    a = int(alpha)
    if a <= 0: return
    for x in range(-144, W+144, 144):
        d.line([x+off, 0, x+off, H], fill=GOLD+(a,))
    off2 = (t*6) % 144
    for y in range(-144, H+144, 144):
        d.line([0, y+off2, W, y+off2], fill=(160, 130, 70, max(0, a-4)))

_VIG = None
def vignette(img):
    global _VIG
    if _VIG is None:
        g = Image.radial_gradient('L').resize((W, H), Image.BILINEAR)
        g = g.point(lambda p: max(0, p-88) * 110 // 167)
        v = Image.new('RGBA', (W, H), (0, 0, 0, 255))
        v.putalpha(g)
        _VIG = v
    img.alpha_composite(_VIG)

def scanlines(img, tl, alpha=16, period=8, speed=60):
    """CRT 扫描线（倒带用）"""
    d = ImageDraw.Draw(img)
    off = int(tl*speed) % period
    for y in range(-period, H+period, period):
        d.line([0, y+off, W, y+off], fill=(200, 220, 255, int(alpha)), width=2)

# ============ 后 FX ============
def _zoom_img(img, s):
    if abs(s-1) < 0.002: return img
    nw, nh = int(W*s), int(H*s)
    img2 = img.resize((nw, nh), Image.BILINEAR)
    x0 = (nw-W)//2; y0 = (nh-H)//2
    return img2.crop((x0, y0, x0+W, y0+H))

def apply_fx(img, tl, fx):
    """fx 字典:
      zoom:  (t0, t1, s0, s1)          持续推镜
      punch: (t0, dur, maxs)            快速缩放冲击
      shake: [(t0, dur, amp), ...]      震屏
      flash: [(t0, dur, color, k), ...] 闪光
    """
    if not fx: return img
    z = fx.get('zoom')
    if z:
        t0, t1, s0, s1 = z
        p = ease(seg(tl, t0, t1))
        img = _zoom_img(img, s0+(s1-s0)*p)
    z = fx.get('punch')
    if z:
        t0, dur, maxs = z
        p = seg(tl, t0, t0+dur)
        if 0 < p < 1:
            img = _zoom_img(img, 1 + (maxs-1)*math.sin(math.pi*p))
    for (t0, dur, amp) in fx.get('shake', []):
        p = seg(tl, t0, t0+dur)
        if 0 < p < 1:
            e = 1-p
            dx = int(amp*e*math.sin((tl-t0)*140))
            dy = int(amp*e*math.cos((tl-t0)*117))
            if dx or dy:
                base = Image.new('RGBA', (W, H), BG+(255,))
                base.paste(img, (dx, dy))
                img = base
    for (t0, dur, color, k) in fx.get('flash', []):
        p = seg(tl, t0, t0+dur)
        if 0 < p < 1:
            ov = Image.new('RGBA', (W, H), color+(int(255*k*(1-p)),))
            img.alpha_composite(ov)
    return img

# ============ 传染网格组件 ============
GRID_COLS, GRID_ROWS = 20, 10
GX0, GY0, GDX, GDY = 124, 268, 88, 76
def grid_pos(gx, gy):
    return GX0 + gx*GDX, GY0 + gy*GDY

def draw_grid(img, tl, flip_times, color=RED, dot_r=11, grid_alpha=1.0,
              pop_dur=0.28, ring=True, preflash=0.16):
    """20x10 点阵传染网格：flip_times[(gx,gy)]=翻转时刻
    v3: preflash>0 时即将翻转的点会预热闪烁"""
    d = ImageDraw.Draw(img)
    ga = clamp01(grid_alpha)
    for gx in range(GRID_COLS):
        for gy in range(GRID_ROWS):
            x, y = grid_pos(gx, gy)
            base_a = 64
            ft = flip_times.get((gx, gy))
            if ft is not None and preflash and 0 < ft - tl <= preflash:
                base_a = 64 + int(130 * math.sin(math.pi * (ft - tl) / preflash))
            d.ellipse([x-dot_r, y-dot_r, x+dot_r, y+dot_r],
                      fill=DIM_DOT+(int(base_a*ga),))
            if ft is not None and tl >= ft:
                p = seg(tl, ft, ft+pop_dur)
                s = back(p)
                r = dot_r*max(0.15, s)
                d.ellipse([x-r, y-r, x+r, y+r], fill=color+(int(235*ga),))
                if ring and p < 1:
                    rr = dot_r + 44*ease_out(p)
                    ra = int(150*(1-p)*ga)
                    if ra > 0:
                        d.ellipse([x-rr, y-rr, x+rr, y+rr], outline=color+(ra,), width=3)

def interp_curve(tl, st, curve):
    """step_times st(len=N+1) 与 curve(len N) 的插值计数器"""
    if tl <= st[0]: return 0.0
    for j in range(len(curve)):
        if tl < st[j+1]:
            f = (tl-st[j])/(st[j+1]-st[j])
            prev = curve[j-1] if j > 0 else 0.0
            return prev + (curve[j]-prev)*f
    return curve[-1]

def flip_map(dots, st):
    """JSON 时刻表 -> {(x,y): 翻转秒}"""
    m = {}
    for d in dots:
        k = d['step']
        t0 = st[k]
        t1 = st[k+1] if k+1 < len(st) else st[-1]+0.6
        m[(d['x'], d['y'])] = t0 + d['off']*(t1-t0)
    return m

# ============ v3 动画增强 ============
def breath(t, freq=1.1, lo=0.0, hi=1.0):
    """呼吸因子：lo..hi 正弦波动"""
    return lo + (hi-lo)*(0.5 + 0.5*math.sin(2*math.pi*freq*t))

def char_pop(img, xy_center, text, font, fill, tl, t0=0.0, stagger=0.13, dur=0.5,
             alpha=1.0, glow=None, glow_radius=22):
    """逐字弹入：每字 0→1.15→1 过冲，自动排布"""
    if tl < t0 or alpha <= 0: return
    lays = [text_layer((int(font.size*3), int(font.size*3)), ch, font, fill, glow, glow_radius)
            for ch in text]
    total_w = sum(l.width for l in lays)
    x = xy_center[0] - total_w/2
    for i, l in enumerate(lays):
        p = seg(tl, t0+i*stagger, t0+i*stagger+dur)
        if p > 0:
            s = back(p)
            if s < 0.995:
                l = l.resize((max(1, int(l.width*s)), max(1, int(l.height*s))),
                             Image.BILINEAR)
            _put_alpha(l, alpha)
            img.alpha_composite(l, (int(x), int(xy_center[1]-l.height/2)))
        x += l.width

def speed_lines(img, cx, cy, tl, t0, dur=0.35, color=WHITE, n=20, alpha=0.5,
                r0=210, r1=560, seed=5):
    """放射状速度线（冲击瞬间）"""
    p = seg(tl, t0, t0+dur)
    if p <= 0: return
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    fade = 1 - p
    for i in range(n):
        ang = 2*math.pi*i/n + rnd.uniform(-0.06, 0.06)
        rr = r1*ease_out(p) + rnd.uniform(-40, 20)
        l0 = r0*(0.75 + 0.25*p) + rnd.uniform(0, 50)
        a = int(255*alpha*fade*rnd.uniform(0.45, 1.0))
        if a > 0 and rr > l0:
            d.line([cx+math.cos(ang)*l0, cy+math.sin(ang)*l0,
                    cx+math.cos(ang)*rr, cy+math.sin(ang)*rr],
                   fill=color+(a,), width=rnd.choice([2, 3, 4]))

def impact_rings(img, cx, cy, tl, t0, color=WHITE, n=2, dur=0.55, r1=280, alpha=190):
    """冲击扩散环"""
    d = ImageDraw.Draw(img)
    for k in range(n):
        p = seg(tl, t0+k*0.1, t0+k*0.1+dur)
        if 0 < p < 1:
            rr = 24 + r1*ease_out(p)
            a = int(alpha*(1-p))
            if a > 0:
                d.ellipse([cx-rr, cy-rr, cx+rr, cy+rr], outline=color+(a,),
                          width=max(2, int(7*(1-p))+2))

def spark_burst(img, cx, cy, tl, t0, color=GOLD, n=16, dur=0.65, speed=380,
                alpha=1.0, seed=1):
    """粒子火花爆开"""
    p = seg(tl, t0, t0+dur)
    if p <= 0: return
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    ee = ease_out(p)
    fade = 1 - p
    for i in range(n):
        ang = rnd.uniform(0, 2*math.pi)
        v = rnd.uniform(0.3, 1.0)
        dist = speed*v*ee
        x = cx + math.cos(ang)*dist
        y = cy + math.sin(ang)*dist*0.8
        a = int(255*clamp01(alpha)*fade*rnd.uniform(0.5, 1.0))
        if a > 0:
            r = rnd.uniform(2.0, 4.8)*(1 - 0.4*p)
            d.ellipse([x-r, y-r, x+r, y+r], fill=color+(a,))

def shine_sweep(img, layer, pos, tl, t0, dur=0.7, color=(255, 255, 255), k=0.7,
                band=None):
    """光泽带扫过文字层（用文字 alpha 做遮罩）"""
    p = seg(tl, t0, t0+dur)
    if not (0 < p < 1): return
    lx, ly = int(pos[0]), int(pos[1])
    w_band = band or max(50, int(layer.width*0.25))
    xc = lx - w_band + (layer.width + 2*w_band)*ease(p)
    band_mask = Image.new('L', layer.size, 0)
    bd = ImageDraw.Draw(band_mask)
    bx0 = int(xc - lx)
    for i in range(w_band):
        a = int(255*math.sin(math.pi*i/w_band))
        bd.line([(bx0+i, 0), (bx0+i, band_mask.height)], fill=a)
    la = layer.split()[3]
    mask = ImageChops.multiply(band_mask, la)
    hl = Image.new('RGBA', layer.size, color+(255,))
    hl.putalpha(mask.point(lambda v: int(v*k)))
    img.alpha_composite(hl, (lx, ly))

def blink_curve(tl, period=2.4, dur=0.24, phase=0.0):
    """周期性眨眼：返回睁眼度 0..1"""
    tt = (tl + phase) % period
    if tt < dur:
        return abs(tt/dur*2 - 1)
    return 1.0

def dash_arrow(img, p0, p1, color, width=6, alpha=1.0, tl=0.0, prog=1.0,
               dash=16, gap=12, head=True):
    """行进虚线箭头（蚂蚁线）"""
    if alpha <= 0 or prog <= 0: return
    d = ImageDraw.Draw(img)
    a = int(255*clamp01(alpha))
    x0, y0 = p0
    x1 = x0 + (p1[0]-x0)*clamp01(prog)
    y1 = y0 + (p1[1]-y0)*clamp01(prog)
    L = math.hypot(x1-x0, y1-y0)
    if L < 4: return
    ux, uy = (x1-x0)/L, (y1-y0)/L
    off = (tl*46) % (dash+gap)
    s = -off
    while s < L:
        e = min(s+dash, L)
        if e > 0:
            sa, ea = max(s, 0), e
            d.line([x0+sa*ux, y0+sa*uy, x0+ea*ux, y0+ea*uy],
                   fill=color+(a,), width=width)
        s += dash+gap
    if head and prog >= 0.999:
        ang = math.atan2(y1-y0, x1-x0)
        Lh = 18
        d.polygon([(x1, y1),
                   (x1+Lh*math.cos(ang+2.67), y1+Lh*math.sin(ang+2.67)),
                   (x1+Lh*math.cos(ang-2.67), y1+Lh*math.sin(ang-2.67))],
                  fill=color+(a,))

def spotlight_cone(img, cx, top_y, bot_y, half_w_top, half_w_bot, tl, t0, dur=0.55,
                   color=GOLD, alpha=0.10):
    """聚光灯锥形光束（柔和渐变）"""
    p = ease_out(seg(tl, t0, t0+dur))
    if p <= 0: return
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    n = 26
    for i in range(n):
        f0, f1 = i/n, (i+1)/n
        a = int(255*alpha*p*(1.0 - 0.55*f0))
        yy0 = top_y + (bot_y-top_y)*f0
        yy1 = top_y + (bot_y-top_y)*f1
        w0 = half_w_top + (half_w_bot-half_w_top)*f0
        w1 = half_w_top + (half_w_bot-half_w_top)*f1
        d.polygon([(cx-w0, yy0), (cx+w0, yy0), (cx+w1, yy1), (cx-w1, yy1)],
                  fill=color+(a,))
    layer = layer.filter(ImageFilter.GaussianBlur(18))
    img.alpha_composite(layer)

_RISE = None
def rising_sparks(img, t, n=20, alpha=80, color=GOLD, seed=8, drift=1.0):
    """上升金色尘埃（金句背景）"""
    global _RISE
    if _RISE is None:
        rnd = random.Random(seed)
        _RISE = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(2.5, 5.5),
                  rnd.uniform(26, 64), rnd.uniform(0, 9)) for _ in range(n)]
    d = ImageDraw.Draw(img)
    for (x0, y0, r, spd, ph) in _RISE:
        y = (y0 - t*spd) % (H+60) - 30
        x = x0 + math.sin(t*0.8 + ph)*18*drift
        a = int(alpha*(0.35 + 0.65*math.sin(t*1.6 + ph*2)))
        if a > 0:
            d.ellipse([x-r, y-r, x+r, y+r], fill=color+(a,))

def sunburst_rays(img, cx, cy, tl, alpha=12, n=28, r1=1150, color=GOLD, rot=0.02):
    """放射光線（标题背景，缓慢旋转）"""
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(n):
        ang = 2*math.pi*i/n + tl*rot
        a = int(alpha*(0.5 + 0.5*math.sin(2*math.pi*3*i/n + tl*0.7)))
        d.polygon([(cx, cy),
                   (cx+math.cos(ang-0.012)*r1, cy+math.sin(ang-0.012)*r1),
                   (cx+math.cos(ang+0.012)*r1, cy+math.sin(ang+0.012)*r1)],
                  fill=color+(a,))
    img.alpha_composite(layer)

def person_idle(img, x, y, size, color, t, phase=0.0, alpha=1.0, is_square=False,
                label=None, label_font=None, amp=3.5):
    """人物待机浮动"""
    draw_person(img, x, y + amp*math.sin(t*2.3 + phase), size, color, alpha,
                is_square, label, label_font)

def draw_check(img, cx, cy, tl, t0, size=70, color=GOLD, width=12, alpha=1.0):
    """对勾自画：两段折线依次生长"""
    p = seg(tl, t0, t0+0.42)
    if p <= 0: return
    d = ImageDraw.Draw(img)
    a = int(255*clamp01(alpha))
    A = (cx-0.36*size, cy+0.05*size)
    B = (cx-0.08*size, cy+0.38*size)
    C = (cx+0.45*size, cy-0.38*size)
    if p < 0.45:
        f = clamp01(p/0.45)
        d.line([A[0], A[1], A[0]+(B[0]-A[0])*f, A[1]+(B[1]-A[1])*f],
               fill=color+(a,), width=width)
    else:
        d.line([A[0], A[1], B[0], B[1]], fill=color+(a,), width=width)
        f = clamp01((p-0.45)/0.55)
        d.line([B[0], B[1], B[0]+(C[0]-B[0])*f, B[1]+(C[1]-B[1])*f],
               fill=color+(a,), width=width)

def wobble(tl, t0, freq=9.0, decay=5.0, amp=1.0):
    """t0 时刻后的阻尼振荡"""
    dt = tl - t0
    if dt < 0: return 0.0
    return amp*math.exp(-decay*dt)*math.sin(2*math.pi*freq*dt)

def step_counter(img, xy_right, value, tl, last_t, font, color, alpha=1.0,
                max_s=1.22, dur=0.24):
    """步进计数器（右上角锚定）：数值变化瞬间弹一下"""
    if alpha <= 0: return
    bump = 1.0
    if last_t is not None:
        p = seg(tl, last_t, last_t+dur)
        if 0 < p < 1:
            bump = 1 + (max_s-1)*math.sin(math.pi*p)
    f = font if bump == 1.0 else font.font_variant(size=int(font.size*bump))
    draw_text_top_a(img, xy_right, value, f, color, alpha, anchor_center=False)
