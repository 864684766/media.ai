"""路由级联（route_cascade + LLM 分类器 + 配置读取）测试。

【覆盖场景】
    1. 配置读取：mode/阈值/关键词覆盖，非法值回退默认。
    2. LLM 输出解析：合法 JSON、带说明文字的 JSON、非法文本。
    3. 级联策略：规则命中不调 LLM；未命中升级 LLM；LLM 失败回退规则；
       mode=rules 永不调 LLM；mode=llm 每次都调。
"""

from app.graph import route_cascade_constants as rc
from app.graph.llm_route_classifier import LlmRouteClassifier
from app.graph.llm_route_parser import parse_route_response
from app.graph.route_cascade import decide_route
from app.graph.route_classifiers import RouteClassifiers
from app.graph.route_settings_reader import RouteSettings, load_route_settings
from app.providers.provider_models import ChatCompletionRequest, ChatCompletionResult
from app.schemas.agent_state import RouteDecision


class RecordingClassifier:
    """记录调用次数的假分类器（模拟 LLM 层）。"""

    def __init__(self, decision: RouteDecision | None) -> None:
        """初始化；decision 为 classify 的固定返回值。"""
        self.decision = decision
        self.calls = 0

    def classify(self, question: str) -> RouteDecision | None:
        """记录调用并返回预设决策。"""
        self.calls += 1
        return self.decision


class FakeProvider:
    """返回固定文本的假 Provider（测试 LlmRouteClassifier 不发真实请求）。"""

    def __init__(self, content: str, error: Exception | None = None) -> None:
        """初始化；error 非空时 chat 抛出该异常。"""
        self._content = content
        self._error = error

    def chat(self, request: ChatCompletionRequest) -> ChatCompletionResult:
        """返回预设文本或抛出预设异常。"""
        if self._error is not None:
            raise self._error
        return ChatCompletionResult(content=self._content, raw={})


# ---------- 配置读取 ----------

def test_route_settings_defaults() -> None:
    """空配置时使用默认：hybrid 模式 + 内置关键词。"""
    settings = load_route_settings({})
    assert settings.mode == rc.ROUTE_MODE_HYBRID
    assert "今天" in settings.keywords.web


def test_route_settings_keyword_override() -> None:
    """app.yaml 可覆盖关键词表，未覆盖的组保持默认。"""
    settings = load_route_settings(
        {"route": {"mode": "rules", "keywords": {"web": ["查询实时"]}}}
    )
    assert settings.mode == rc.ROUTE_MODE_RULES
    assert settings.keywords.web == ("查询实时",)
    assert "续写" in settings.keywords.creative


def test_route_settings_invalid_mode_falls_back() -> None:
    """非法 mode 回退默认 hybrid。"""
    settings = load_route_settings({"route": {"mode": "magic"}})
    assert settings.mode == rc.ROUTE_MODE_HYBRID


# ---------- LLM 输出解析 ----------

def test_parse_valid_json() -> None:
    """合法 JSON 解析成 RouteDecision。"""
    decision = parse_route_response(
        '{"needs_project": true, "needs_web": false, "needs_creative": true,'
        ' "sub_queries": ["张三 师父"], "reason": "查设定并续写"}'
    )
    assert decision is not None
    assert decision.needs_project and decision.needs_creative
    assert decision.sub_queries == ["张三 师父"]
    assert decision.confidence == rc.LLM_ROUTE_CONFIDENCE


def test_parse_json_wrapped_in_text() -> None:
    """模型在 JSON 外包了说明文字/代码块也能解析。"""
    decision = parse_route_response(
        '好的，判定如下：\n```json\n{"needs_web": true, "needs_project": false,'
        ' "needs_creative": false, "sub_queries": [], "reason": "查时效"}\n```'
    )
    assert decision is not None and decision.needs_web


def test_parse_invalid_text_returns_none() -> None:
    """非 JSON 文本解析失败返回 None（由级联回退规则层）。"""
    assert parse_route_response("抱歉我不明白") is None


# ---------- LlmRouteClassifier ----------

def test_classifier_provider_error_returns_none() -> None:
    """Provider 抛异常时 classify 返回 None 而不是向上抛。"""
    classifier = LlmRouteClassifier(FakeProvider("", error=RuntimeError("超时")))
    assert classifier.classify("问题") is None


def _llm_bundle(recorder: RecordingClassifier) -> RouteClassifiers:
    """将假分类器包装为 RouteClassifiers（仅 L3）。"""
    return RouteClassifiers(llm=recorder)  # type: ignore[arg-type]


# ---------- 级联策略 ----------

def _hybrid_settings() -> RouteSettings:
    """hybrid 模式 + 默认阈值 0.6 的测试配置。"""
    return RouteSettings(mode=rc.ROUTE_MODE_HYBRID)


def test_hybrid_rule_hit_skips_llm() -> None:
    """规则命中（置信度 0.6 >= 阈值 0.6）时不调 LLM。"""
    classifier = RecordingClassifier(None)
    decision = decide_route("帮我续写一段", _llm_bundle(classifier), _hybrid_settings())
    assert classifier.calls == 0
    assert decision.needs_creative


def test_hybrid_no_hit_escalates_to_llm() -> None:
    """规则未命中（置信度 0.5 < 0.6）时升级 LLM 并采用其结果。"""
    llm_decision = RouteDecision(needs_web=True, reason=rc.LLM_ROUTE_REASON)
    classifier = RecordingClassifier(llm_decision)
    decision = decide_route("北宋的官制是怎样的", _llm_bundle(classifier), _hybrid_settings())
    assert classifier.calls == 1
    assert decision.needs_web and decision.reason == rc.LLM_ROUTE_REASON


def test_hybrid_llm_failure_falls_back_to_rules() -> None:
    """LLM 返回 None 时回退规则结果并标注回退原因。"""
    classifier = RecordingClassifier(None)
    decision = decide_route("北宋的官制是怎样的", _llm_bundle(classifier), _hybrid_settings())
    assert classifier.calls == 1
    assert decision.needs_creative  # 规则层默认创作通道
    assert rc.LLM_FALLBACK_REASON_SUFFIX in decision.reason


def test_rules_mode_never_calls_llm() -> None:
    """mode=rules 即使注入了分类器也不调用。"""
    classifier = RecordingClassifier(RouteDecision(needs_web=True))
    settings = RouteSettings(mode=rc.ROUTE_MODE_RULES)
    decide_route("北宋的官制是怎样的", _llm_bundle(classifier), settings)
    assert classifier.calls == 0


def test_llm_mode_always_calls_llm() -> None:
    """mode=llm 时规则命中也会问 LLM。"""
    llm_decision = RouteDecision(needs_project=True, reason=rc.LLM_ROUTE_REASON)
    classifier = RecordingClassifier(llm_decision)
    settings = RouteSettings(mode=rc.ROUTE_MODE_LLM)
    decision = decide_route("帮我续写一段", _llm_bundle(classifier), settings)
    assert classifier.calls == 1
    assert decision.needs_project
