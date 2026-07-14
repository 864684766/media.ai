"""LangGraph 图常量。

【职责】
    集中管理图中节点名字面量，避免在多个文件里手写字符串。

【何时被调用】
    app/graph/langgraph_builder.py 组图时引用；
    测试断言节点名时也应引用本文件，保证改名只改一处。
"""

# 节点名：加载 Skill（读 skills/ 目录，写 state.skill）
NODE_LOAD_SKILL = "load_skill"

# 节点名：加载会话历史（读 PG，写 state.history）
NODE_LOAD_HISTORY = "load_history"

# 节点名：路由决策（写 state.route，输出 needs_* 能力开关）
NODE_ROUTE_QUESTION = "route_question"

# 节点名：检索链（needs_project / needs_web 时执行，写 state.retrieval）
NODE_RETRIEVE_CONTEXT = "retrieve_context"

# 条件边分支名：需要检索 / 直接进入 compact（route_question 之后的走向）
BRANCH_RETRIEVE = "retrieve"
BRANCH_SKIP_RETRIEVE = "skip_retrieve"

# 节点名：压缩历史并拼装 prompt（写 state.prompt）
NODE_COMPACT_HISTORY = "compact_history"

# 节点名：调用 Provider 生成回答（写 state.answer）
NODE_GENERATE = "generate"

# 节点名：持久化本轮消息（写 state.message_ids）
NODE_SAVE_MESSAGES = "save_messages"

# 无数据库时 save_messages 返回的占位消息 id（本地开发/测试用，非真实持久化）
MEMORY_MESSAGE_ID_USER = "memory:user"
MEMORY_MESSAGE_ID_ASSISTANT = "memory:assistant"
