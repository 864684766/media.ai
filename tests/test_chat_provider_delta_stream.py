"""Chat Provider delta stream 测试。"""

import pytest

from app.providers.provider_stream_models import ProviderStreamChunk
from app.schemas.agent_state import AgentState
from app.schemas.chat import ChatRequest
from app.graph.state_factory import create_initial_state
from app.services.chat_provider_delta_stream import yield_provider_delta_frames


def test_yield_provider_delta_frames_outputs_usage(monkeypatch: pytest.MonkeyPatch) -> None:
    """Provider usage chunk 应转为 SSE usage 事件。"""

    def fake_events(state: AgentState):
        yield ProviderStreamChunk(delta="你")
        yield ProviderStreamChunk(usage={"total_tokens": 9})

    monkeypatch.setattr(
        "app.services.chat_provider_delta_stream.stream_provider_answer_events",
        fake_events,
    )
    state = create_initial_state(ChatRequest(message="你好"))
    frames = list(yield_provider_delta_frames(state))
    assert "event: content_delta" in frames[0]
    assert "event: usage" in frames[1]
