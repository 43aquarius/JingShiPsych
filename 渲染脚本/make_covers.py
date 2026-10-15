#!/usr/bin/env python3
"""封面生成：横屏 16:9 (2400x1350) + 竖屏 9:16 (1080x1920)
仿原片封面结构：顶部悬念主标题 + 切角副标题面板 + 三列数据对比 + 底部数据方块
"""
import math
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import sys
sys.path.insert(0, '/home/z/my-project/scripts')
from render_lib import GOLD, GOLD_HI, GOLD_DK, RED, RED_DK, WHITE, GRAY, GRAY_DK, CYAN, serif, mono, BG

SERIF = '/usr/share/fonts/truetype/noto-serif-sc'
OUT = '/home/z/my-project/download'

def chamfer_panel(d, box, cut, fill, outline=None, width=3):
    """切角面板（HUD 风格）"""
    x0, y0, x1, y1 = box
    pts = [(x0+cut, y0), (x1, y0), (x1, y1-cut), (x1-cut, y1), (x0, y1), (x0, y0+cut)]
    d.polygon(pts, fill=fill)
    if outline:
        d.line(pts+[pts[0]], fill=outline, width=width, joint='curve')

def glow_text(img, xy_center, text, font, fill, glow_color, radius=30, alpha=1.0):
    """发光文字（封面版：更大半径）"""
    tmp = Image.new('RGBA', (int(img.width*1.2), int(font.size*3)), (0,0,0,0))
    d = ImageDraw.Draw(tmp)
    bbox = d.textbbox((0,0), text, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    if glow_color:
        g = Image.new('RGBA', tmp.size, (0,0,0,0))
        gd = ImageDraw.Draw(g)
        gd.text((-bbox[0], -bbox[1]), text, font=font, fill=glow_color+(230,))
        g = g.filter(ImageFilter.GaussianBlur(radius))
        tmp.alpha_composite(g)
    d = ImageDraw.Draw(tmp)
    d.text((-bbox[0], -bbox[1]), text, font=font, fill=fill+(255,))
    bbox2 = tmp.getbbox()
    tmp = tmp.crop(bbox2)
    if alpha < 1:
        a = tmp.split()[3].point(lambda p: int(p*alpha))
        tmp.putalpha(a)
    img.alpha_composite(tmp, (int(xy_center[0]-tmp.width/2), int(xy_center[1]-tmp.height/2)))
    return tmp

def pixel_strip(d, x, y, w, h, cells, gap=5):
    n = len(cells)
    cw = (w - gap*(n-1)) / n
    for i, c in enumerate(cells):
        if c is None: continue
        cx = x + i*(cw+gap)
        d.rounded_rectangle([cx, y, cx+cw, y+h], radius=3, fill=c)

def bg_texture(w, h, seed=42):
    """黑底 + 微弱金色放射线 + 点阵"""
    import random
    img = Image.new('RGBA', (w, h), BG+(255,))
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    cx, cy = w*0.5, h*0.42
    # 放射线
    for i in range(48):
        ang = 2*math.pi*i/48 + rnd.random()*0.06
        L = max(w, h)*1.5
        a = rnd.randint(8, 22)
        d.line([cx, cy, cx+L*math.cos(ang), cy+L*math.sin(ang)], fill=(255,194,77,a), width=2)
    # 微点阵
    for _ in range(int(w*h/9000)):
        x, y = rnd.random()*w, rnd.random()*h
        d.ellipse([x, y, x+2, y+2], fill=(255,194,77,rnd.randint(8,26)))
    # 暗角
    vign = Image.new('L', (w, h), 0)
    dv = ImageDraw.Draw(vign)
    dv.ellipse([cx-w*0.7, cy-h*0.75, cx+w*0.7, cy+h*0.75], fill=90)
    vign = vign.filter(ImageFilter.GaussianBlur(180))
    black = Image.new('RGBA', (w, h), (0,0,0,255))
    img = Image.composite(img, black, vign.point(lambda p: 255-p)).convert('RGBA')
    img.putalpha(Image.new('L', (w, h), 255))
    return img

# ================= 横屏封面 2400x1350 =================
def cover_landscape():
    W, H = 2400, 1350
    img = bg_texture(W, H)
    d = ImageDraw.Draw(img)

    # --- 顶部主标题（悬念反差） ---
    # 「37% 的人」红 + 「，跟着说错了。」白
    f_main = serif('BK', 170)
    parts = [('37% 的人', RED), ('，跟着说错了。', WHITE)]
    tmp = Image.new('RGBA', (W, 500), (0,0,0,0))
    # 手动多色混排
    td = ImageDraw.Draw(tmp)
    xoff = 0
    layers = []
    for txt, col in parts:
        t2 = Image.new('RGBA', (int(W), 600), (0,0,0,0))
        d2 = ImageDraw.Draw(t2)
        bb = d2.textbbox((0,0), txt, font=f_main)
        t2w, t2h = bb[2]-bb[0], bb[3]-bb[1]
        if col == RED:
            g = Image.new('RGBA', t2.size, (0,0,0,0))
            gd = ImageDraw.Draw(g)
            gd.text((-bb[0], -bb[1]), txt, font=f_main, fill=RED+(160,))
            g = g.filter(ImageFilter.GaussianBlur(40))
            t2.alpha_composite(g)
        d2.text((-bb[0], -bb[1]), txt, font=f_main, fill=col+(255,))
        bb2 = t2.getbbox()
        t2 = t2.crop(bb2)
        layers.append((t2, xoff))
        xoff += t2.width + 8
    total_w = xoff - 8
    base_x = W/2 - total_w/2
    for layer, xo in layers:
        img.alpha_composite(layer, (int(base_x+xo), 150))

    # --- 中部切角副标题面板 ---
    panel_y0, panel_y1 = 540, 680
    pw = 1500
    px0 = W/2 - pw/2
    chamfer_panel(d, [px0, panel_y0, px0+pw, panel_y1], 26, (22, 22, 25, 235), outline=GOLD_DK if 'GOLD_DK' in dir() else (120,95,45), width=2)
    # 副标题
    f_sub = serif('M', 74)
    sub = '从众心理实验《三人成虎》'
    bb = d.textbbox((0,0), sub, font=f_sub)
    sw, sh = bb[2]-bb[0], bb[3]-bb[1]
    d.text((W/2-sw/2, (panel_y0+panel_y1)/2-sh/2-6), sub, font=f_sub, fill=GOLD_HI+(255,))

    # --- 三列数据对比 ---
    cols = [
        ('独自作答', '0.7%', WHITE,  '几乎不错'),
        ('7 人齐错', '37%',  RED,   '跟着说错'),
        ('1 人真话', '5%',   GOLD_HI, '人群清醒'),
    ]
    col_w, gap_w = 620, 60
    total_cw = col_w*3 + gap_w*2
    x_start = W/2 - total_cw/2
    y_top = 800
    # 竖分割线
    for i in range(2):
        lx = x_start + col_w*(i+1) + gap_w*i + gap_w/2
        d.line([lx, y_top-30, lx, y_top+330], fill=(90, 70, 30, 160), width=3)
    for i, (label, num, color, tag) in enumerate(cols):
        cx = x_start + (col_w+gap_w)*i + col_w/2
        f_lab = serif('L', 56)
        draw_text = label
        bb = d.textbbox((0,0), draw_text, font=f_lab)
        lw, lh = bb[2]-bb[0], bb[3]-bb[1]
        d.text((cx-lw/2, y_top), draw_text, font=f_lab, fill=(185,185,190,255))
        # 数字（发光）
        f_num = mono('B', 150)
        glow_text(img, (cx, y_top+230), num, f_num, color, color if color != WHITE else None, radius=36)
        # 标签
        f_tag = serif('R', 48)
        bb = d.textbbox((0,0), tag, font=f_tag)
        tw, th = bb[2]-bb[0], bb[3]-bb[1]
        d.text((cx-tw/2, y_top+390), tag, font=f_tag, fill=(140,140,145,255))

    # --- 底部数据方块条 ---
    y_bar = 1290
    strips = [
        [RED]*2 + [None]*10,                 # 独自（几乎全对）
        [RED if (j%3==0) else RED_DK for j in range(12)],  # 37%
        [GOLD]*1 + [GOLD_DK]*11,             # 5%
    ]
    for i, cells in enumerate(strips):
        sx = x_start + (col_w+gap_w)*i + col_w/2 - 280
        pixel_strip(d, sx, y_bar-40, 560, 44, cells, gap=6)

    img = img.convert('RGB')
    img.save(f'{OUT}/封面_横屏_三人成虎.png', quality=95)
    print('横屏封面完成', img.size)

# ================= 竖屏封面 1080x1920 =================
def cover_portrait():
    W, H = 1080, 1920
    img = bg_texture(W, H, seed=7)
    d = ImageDraw.Draw(img)

    # 顶部小标签
    f_tag = serif('R', 44)
    tag = '—— 1951 年真实心理学实验 ——'
    bb = d.textbbox((0,0), tag, font=f_tag)
    d.text((W/2-(bb[2]-bb[0])/2, 170), tag, font=f_tag, fill=GRAY+(255,))

    # 主标题竖排：37% 超大
    glow_text(img, (W/2, 420), '37%', mono('B', 300), RED, RED, radius=50)
    f_line = serif('BK', 130)
    glow_text(img, (W/2, 640), '的人', f_line, WHITE, None)
    glow_text(img, (W/2, 780), '跟着说错了', f_line, WHITE, None)

    # 切角副标题面板
    pw, ph = 860, 130
    px0 = W/2-pw/2
    chamfer_panel(d, [px0, 950, px0+pw, 950+ph], 22, (22,22,25,235), outline=(120,95,45), width=2)
    f_sub = serif('M', 62)
    sub = '从众心理实验《三人成虎》'
    bb = d.textbbox((0,0), sub, font=f_sub)
    d.text((W/2-(bb[2]-bb[0])/2, 950+ph/2-(bb[3]-bb[1])/2-4), sub, font=f_sub, fill=GOLD_HI+(255,))

    # 三行数据对比（竖排）
    rows = [
        ('独自作答', '0.7%', WHITE,  [None]*11 + [RED]*1, '几乎不错'),
        ('7 人齐错', '37%',  RED,   [RED if (j%3==0) else RED_DK for j in range(12)], '跟着说错'),
        ('1 人真话', '5%',   GOLD_HI, [GOLD] + [GOLD_DK]*11, '人群清醒'),
    ]
    y = 1160
    for label, num, color, cells, tag in rows:
        f_lab = serif('L', 58)
        d.text((120, y), label, font=f_lab, fill=(200,200,204,255))
        f_num = mono('B', 110)
        bb = d.textbbox((0,0), num, font=f_num)
        d.text((W-120-(bb[2]-bb[0]), y-14), num, font=f_num, fill=color+(255,))
        # 像素条
        pixel_strip(d, 120, y+100, 840, 40, cells, gap=7)
        # 分隔
        d.line([120, y+170, W-120, y+170], fill=(60,60,64,180), width=2)
        y += 230

    # 底部金句
    glow_text(img, (W/2, 1830), '你有眼睛。', serif('BK', 96), GOLD_HI, GOLD, radius=34)

    img = img.convert('RGB')
    img.save(f'{OUT}/封面_竖屏_三人成虎.png', quality=95)
    print('竖屏封面完成', img.size)

if __name__ == '__main__':
    cover_landscape()
    cover_portrait()
