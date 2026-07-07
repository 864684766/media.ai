/**
 * MCP / RAG / ToolNode 集成流程图（第 11 章）
 * 职责：展示 LangGraph 内 RAG 与 MCP 工具并行汇入上下文
 */

/** @type {object} MCP 集成流程图规格 */
var MCP_FLOW_SPEC = {
  mountId: 'flow-mcp-root',
  buildNodes: buildMcpFlowNodes,
  buildEdges: buildMcpFlowEdges,
  minZoom: 0.18
};

/**
 * 构建 MCP 集成节点
 * @returns {Array<object>} 节点数组
 */
function buildMcpFlowNodes() {
  var cx = 340;
  var dy = 100;
  return [
    mainNode('user', 'input', cx, 0, '用户问题', '#dbeafe', '#2563eb'),
    mainNode('lg', 'default', cx, dy, 'LangGraph', '#dcfce7', '#16a34a'),
    customDecisionNode('router', cx - 14, dy * 2, 'Adaptive Router'),
    chainNode('rag', 40, dy * 3.2, 'RAG 检索链\nLangChain Retriever', '#fef3c7', '#d97706'),
    chainNode('tool', 640, dy * 3.2, 'ToolNode', '#e0e7ff', '#4338ca'),
    dbNode('neo', 20, dy * 4.6, 'Neo4j'),
    dbNode('pg', 20, dy * 5.6, 'PostgreSQL'),
    sideNode('builtin', 640, dy * 4.6, '内置工具\nWeb Search', '#ffedd5', '#ea580c'),
    sideNode('mcp', 640, dy * 5.6, 'MCP Tools', '#e0e7ff', '#4338ca'),
    sideNode('ext', 860, dy * 5.6, '外部 MCP Server\nstdio/HTTP', '#f1f5f9', '#64748b'),
    mainNode('ctx', 'default', cx, dy * 5.2, '合并上下文', '#dcfce7', '#16a34a'),
    mainNode('llm', 'output', cx, dy * 6.4, 'LLM 生成', '#ede9fe', '#7c3aed')
  ];
}

/**
 * 构建 MCP 集成边
 * @returns {Array<object>} 边数组
 */
function buildMcpFlowEdges() {
  return [
    flowEdge('m1', 'user', 'lg', ''),
    flowEdge('m2', 'lg', 'router', ''),
    branchEdge('m3a', 'router', 'rag', '需要私有知识', BRANCH_A_COLOR, 'left'),
    branchEdge('m3b', 'router', 'tool', '需要外部动作', BRANCH_B_COLOR, 'right'),
    sideEdge('m4a', 'rag', 'neo', '向量检索', 'left'),
    sideEdge('m4b', 'rag', 'pg', '全文检索', 'left'),
    sideEdge('m5a', 'tool', 'builtin', 'Web', 'right'),
    sideEdge('m5b', 'tool', 'mcp', 'MCP 调用', 'right'),
    sideEdge('m5c', 'mcp', 'ext', '协议', 'right'),
    mergeEdge('m6a', 'rag', 'ctx', 'RAG 上下文', 'left'),
    mergeEdge('m6b', 'tool', 'ctx', '工具结果', 'right'),
    flowEdge('m7', 'ctx', 'llm', '')
  ];
}
