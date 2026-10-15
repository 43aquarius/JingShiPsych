#!/usr/bin/env python3
"""最终合成 v3：render/video_v3.mp4（无音轨）+ BGM（原片音轨）→ 成片
- 视频流直接 copy（v3 已在渲染时完成 x264 编码）
- 音频：原片音轨 0-147s，头部 0.4s 淡入，尾部 142.6s 起 4.4s 淡出
"""
import subprocess, os, json

SRC_VID = '/home/z/my-project/render/video_v3.mp4'
BGM = '/home/z/my-project/source_video/bgm_original.m4a'
OUT = '/home/z/my-project/download/三人成虎_从众心理学_1080p.mp4'
DUR = 147.0

af = ('atrim=0:147,asetpts=PTS-STARTPTS,'
      'afade=t=in:st=0:d=0.4,afade=t=out:st=142.6:d=4.4,volume=1.0')

cmd = [
    'ffmpeg', '-y', '-loglevel', 'error',
    '-i', SRC_VID, '-i', BGM,
    '-t', str(DUR),
    '-c:v', 'copy',
    '-c:a', 'aac', '-b:a', '192k',
    '-af', af,
    '-shortest',
    OUT,
]
print('开始合成...')
# 注意：IO 全重定向，避免 ffmpeg 输出管道挂起导致假超时
log = open('/home/z/my-project/render/assemble_v3.log', 'w')
subprocess.run(cmd, stdout=log, stderr=log)
size = os.path.getsize(OUT) / 1024 / 1024
print(f'合成完成: {OUT} ({size:.1f} MB)')

probe = subprocess.check_output([
    'ffprobe', '-v', 'quiet', '-show_entries',
    'format=duration,size:stream=codec_name,width,height,r_frame_rate',
    '-of', 'json', OUT
]).decode()
print(json.dumps(json.loads(probe), indent=2, ensure_ascii=False))
