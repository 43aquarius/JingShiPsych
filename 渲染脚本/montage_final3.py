#!/usr/bin/env python3
"""v3 成片抽帧质检：均匀抽 30 帧 -> 3 张总览图"""
import subprocess, os
from PIL import Image, ImageDraw, ImageFont

VID = '/home/z/my-project/download/三人成虎_从众心理学_1080p.mp4'
SRC = '/home/z/my-project/render/final_check3'
os.makedirs(SRC, exist_ok=True)

# 均匀抽 30 帧（避开首尾纯黑）
ts = [147*i/31 + 1.2 for i in range(30)]
for i, t in enumerate(ts):
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', f'{t:.2f}',
                    '-i', VID, '-frames:v', '1', f'{SRC}/f{t:06.2f}.png'],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
files = sorted(os.listdir(SRC))
print('抽帧', len(files))

OUT = '/home/z/my-project/render/final_check3_sheets'
os.makedirs(OUT, exist_ok=True)
cols, rows = 3, 4
TW, TH = 640, 360
font = ImageFont.truetype('/usr/share/fonts/truetype/chinese/SarasaMonoSC-Regular.ttf', 22)
for s in range(0, len(files), cols*rows):
    grp = files[s:s+cols*rows]
    sheet = Image.new('RGB', (cols*TW, rows*TH), (10, 10, 12))
    d = ImageDraw.Draw(sheet)
    for k, f in enumerate(grp):
        im = Image.open(f'{SRC}/{f}').resize((TW, TH), Image.BILINEAR)
        r, c = divmod(k, cols)
        sheet.paste(im, (c*TW, r*TH))
        d.rectangle([c*TW, r*TH, c*TW+80, r*TH+28], fill=(0, 0, 0))
        d.text((c*TW+6, r*TH+3), f[1:-4]+'s', font=font, fill=(255, 220, 140))
        d.rectangle([c*TW, r*TH, c*TW+TW-1, r*TH+TH-1], outline=(40, 40, 44), width=1)
    sheet.save(f'{OUT}/fsheet_{s//(cols*rows)+1}.jpg', quality=88)
    print('sheet', s//(cols*rows)+1, len(grp))
