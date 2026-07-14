"""视频音频域常量（V8 一处权威）。

【职责】
    audio_assets.track_type、source、文件名等字面量。

【何时调用】
    TTS Stub、compose 时间轴、API 契约共用。
"""

# audio_assets.track_type
TRACK_TYPE_DIALOGUE = "dialogue"
TRACK_TYPE_BGM = "bgm"
TRACK_TYPE_SFX = "sfx"

# audio_assets.source
AUDIO_SOURCE_TTS = "tts"
AUDIO_SOURCE_LIBRARY = "library"
AUDIO_SOURCE_UPLOAD = "upload"

# 默认 TTS Provider（app.yaml 可覆盖）
DEFAULT_TTS_PROVIDER = "stub"

# 落盘文件名
DIALOGUE_WAV_FILENAME = "dialogue.wav"
SUBTITLE_SRT_FILENAME = "subtitles.srt"

# 默认 voice_id（角色未配置时）
DEFAULT_VOICE_ID = "default"
