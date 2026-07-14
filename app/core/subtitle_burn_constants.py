"""字幕烧录 ffmpeg 常量（阶段 G3）。"""

# 烧录后视频编码
SUBTITLE_BURN_VIDEO_CODEC = "libx264"
SUBTITLE_BURN_PRESET = "fast"
SUBTITLE_BURN_CRF = "23"

# subtitles 滤镜 force_style（底部白字黑边）
SUBTITLE_FORCE_STYLE = "FontSize=20,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=2"
