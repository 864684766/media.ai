"""视频子图节点名常量（V6 编排引用，一处权威）。

【职责】
    与 VIDEO_PIPELINE §4 子图节点对齐；后续 LangGraph 组图时 import。
"""

# 子图节点：结构化分镜入库
NODE_STORYBOARD_JSON = "storyboard_json"
# 子图节点：实体校验
NODE_VALIDATE_ENTITIES = "validate_entities"
# 子图节点：HITL 审核门
NODE_REVIEW_GATE = "review_gate"
# 子图节点：关键帧渲染
NODE_RENDER_KEYFRAMES = "render_keyframes"
# 子图节点：切片渲染
NODE_RENDER_SHOTS = "render_shots"
# 子图节点：连续性 QA
NODE_CONTINUITY_CHECK = "continuity_check"
# 子图节点：时间轴合成
NODE_COMPOSE = "compose"
# 子图节点：音频与字幕（V8）
NODE_AUDIO_PIPELINE = "audio_pipeline"
