"""视频音频 API 契约（V8）。"""

from pydantic import BaseModel, Field


class AudioAssetOutput(BaseModel):
    """单条音频资产。"""

    audio_id: str = Field(description="音频 id")
    shot_id: str = Field(description="绑定镜头，BGM 可为空")
    track_type: str = Field(description="dialogue/bgm/sfx")
    uri: str = Field(description="相对 files 路径")
    duration_sec: float = Field(description="时长秒")
    voice_id: str = Field(description="TTS 音色 id")
    open_url: str = Field(description="inline 打开 URL")
    download_url: str = Field(description="下载 URL")


class AudioPipelineResponse(BaseModel):
    """POST /audio 响应。"""

    project_id: str = Field(description="项目 id")
    dialogue_count: int = Field(description="生成的对白轨数量")
    subtitle_uri: str = Field(description="SRT 相对 URI")
    subtitle_open_url: str = Field(description="字幕打开 URL")
    assets: list[AudioAssetOutput] = Field(default_factory=list)
    tts_provider: str = Field(default="stub", description="实际 TTS Provider")


class AudioTracksListResponse(BaseModel):
    """GET /audio/tracks 响应。"""

    project_id: str = Field(description="项目 id")
    items: list[AudioAssetOutput] = Field(default_factory=list)


class BgmUploadResponse(BaseModel):
    """POST /audio/bgm 响应。"""

    project_id: str = Field(description="项目 id")
    audio_id: str = Field(description="BGM 音频 id")
    uri: str = Field(description="相对 files 路径")
    duration_sec: float = Field(description="时长秒")
    open_url: str = Field(description="inline URL")
    download_url: str = Field(description="下载 URL")
