"""Profile 套餐（L2 配置层）。

【本文件职责】
    定义 dev / prod / strict 三档「默认运行时参数」。
    运维只需在 config/app.yaml 写 profile: prod，不必记每个数字。

【与 app.yaml 的关系】
    app.yaml 的 model、skills 等段 → 留给 Provider、Registry 等模块读（本文件不管）
    app.yaml 的 profile 键 → 决定从下面哪一行套餐拷贝参数

【示例】
    profile: dev  → max_retries=2, retrieve_top_k=30, refuse_when_no_evidence=False
    profile: strict → rerank_top_k=3, refuse_when_no_evidence=True（更谨慎）
"""

from app.core import config_constants as cc

# 三档 Profile 的默认运行时参数（不含 profile 字段本身，profile 由 resolve 单独写入）
PROFILE_PRESETS: dict[str, dict[str, int | str | bool]] = {
    # 开发档：召回少一些，跑得快，便于本地调试
    cc.PROFILE_DEV: {
        cc.FIELD_MAX_RETRIES: 2,
        cc.FIELD_RETRIEVE_TOP_K: 30,
        cc.FIELD_RERANK_TOP_K: 5,
        cc.FIELD_GRAPH_EXPAND_HOPS: 2,
        cc.FIELD_WEB_SEARCH: cc.WEB_SEARCH_CONDITIONAL,
        cc.FIELD_REFUSE_WHEN_NO_EVIDENCE: False,
    },
    # 生产档：召回更多，答案更全
    cc.PROFILE_PROD: {
        cc.FIELD_MAX_RETRIES: 2,
        cc.FIELD_RETRIEVE_TOP_K: 50,
        cc.FIELD_RERANK_TOP_K: 5,
        cc.FIELD_GRAPH_EXPAND_HOPS: 2,
        cc.FIELD_WEB_SEARCH: cc.WEB_SEARCH_CONDITIONAL,
        cc.FIELD_REFUSE_WHEN_NO_EVIDENCE: False,
    },
    # 严格档：证据不足时可拒答，适合对幻觉敏感的场景
    cc.PROFILE_STRICT: {
        cc.FIELD_MAX_RETRIES: 3,
        cc.FIELD_RETRIEVE_TOP_K: 50,
        cc.FIELD_RERANK_TOP_K: 3,
        cc.FIELD_GRAPH_EXPAND_HOPS: 2,
        cc.FIELD_WEB_SEARCH: cc.WEB_SEARCH_CONDITIONAL,
        cc.FIELD_REFUSE_WHEN_NO_EVIDENCE: True,
    },
}
