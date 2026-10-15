# 三人成虎 · 从众心理学（JingShiPsych）

仿 B 站《以牙还牙》（BV1X8a16wEGh）风格的**黑金极简数据可视化心理学科普动画**。

- **主题**：从众效应（Conformity）——为什么明知答案，你还是跟着说错？
- **成片**：2 分 27 秒 · 1920×1080 @ 30fps · H.264 + AAC · 纯字幕 + BGM（无旁白）
- **制作方式**：49 个场景、4410 帧画面，全部由自研 Python/PIL 渲染引擎逐帧绘制，非模板套用
- **数据真实**：画面中的传染曲线来自 Granovetter 阈值模型的 500 人真实模拟，实验数据出自 Asch 1956 等经典文献

---

## 影片结构

| 幕 | 内容 | 视觉手法 |
|---|------|---------|
| 冷开场 | 6 连切悬念：线段测验 → 7 人齐错 → 37% → 眼睛没问题 | 卡尺扫描线、方块残影下落+落地挤压+火花、速度线、眼睛呼吸光晕 |
| 标题 | 《三人成虎》揭示 | 放射光线背景 + 逐字弹入 + 光泽扫字 |
| 实验重演 | 1951 阿希线段实验：8 人入座 → 投票大戏 → 轮到你 | 待机浮动、发言人浮起+声波弧、聚光灯锥+人物颤抖+打字光标 |
| 数据冲击 | 0.7% vs 37%（×50 倍）→ 75% 人墙 → 信息性/规范性从众 | 条形高光带、冲击环、步进弹跳计数、行进虚线 |
| 传染 | 阈值仪表 → 200 点网格 13 步雪崩至 75% | 网格预热闪烁、粒子翻转、步进计数 |
| 解药 | 倒带 → 放进一个说真话的人 → 同盟防火墙 → 37%→5% | 时间码回滚、金点天降拖尾+冲击波、双层旋转护罩 |
| 四把钥匙 | 先写 / 慢说 / 出声 / 回看 | 时钟跳格过冲、声波+气泡、眨眼曲线 |
| 结尾升华 | 金句三连 → 「你有眼睛。」 | 上升尘埃、呼吸缩放、双眨眼+星形反光+光泽扫字 |

## 仓库结构

```
├── 成片/       三人成虎_从众心理学_1080p.mp4（147s，25.7MB）
├── 封面/       横屏 2400×1350 / 竖屏 1080×1920（B 站规格）
├── 发布文案/   标题（3 选 1）+ 简介 + BGM 说明 + 数据出处
├── 渲染脚本/   完整渲染管线（Python 3 + Pillow）
└── 数据/       传染模拟、网格时刻表、BGM 能量分析
```

## 渲染复现

```bash
pip install pillow            # 唯一依赖（字体用系统 Noto Serif SC / Sarasa Mono SC）
python3 渲染脚本/contagion_sim.py    # ① 跑 Granovetter 阈值模型模拟
python3 渲染脚本/infection_grid.py   # ② 生成 20×10 网格翻转时刻表
python3 渲染脚本/render_video.py --encode   # ③ 逐帧渲染 + 管道编码（约 4 分钟）
python3 渲染脚本/assemble.py          # ④ 与 BGM 合成成片
```

> 脚本内的绝对路径对应渲染工作机目录（`/home/z/my-project/...`），复现时请按需替换。
> BGM 直接提取自参考视频《以牙还牙》的纯音乐音轨（原片无人声），仅作风格研究与个人学习用途。

## 核心数据出处

- ASCH, S. E. (1956). Studies of independence and conformity: A minority of one against a unanimous majority. *Psychological Monographs*, 70(9).
- GRANOVETTER, M. (1978). Threshold Models of Collective Behavior. *American Journal of Sociology*, 83(6).
- ALLEN, V. L. & LEVINE, J. M. (1971). Social Support and Conformity: The Role of Independent Assessment of Reality. *JPSP*.
- DEUTSCH, M. & GERARD, H. B. (1955). A Study of Normative and Informational Social Influences. *Abnormal and Social Psychology*, 51(3).

## 致谢

- 参考片源：B 站《以牙还牙！——为什么说善良的大多数，总会输给一小撮坏人？》（BV1X8a16wEGh）
- 分析工具：[ztough926/video-understanding](https://github.com/ztough926/video-understanding) 关键帧抽取
