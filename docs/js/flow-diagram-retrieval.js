/**
 * 检索准确性工程流程图（第 7 章）
 * 职责：展示 Hybrid→Grader→Rerank 顺序、Rewrite 回路、Web 兜底与幻觉检测
 */

/** @type {object} 检索工程流程图规格 */
var RETRIEVAL_FLOW_SPEC = {
  mountId: 'flow-retrieval-root',
  buildNodes: buildRetrievalFlowNodes,
  buildEdges: buildRetrievalFlowEdges,
  minZoom: 0.15
};

/**
 * 构建检索工程节点
 * @returns {Array<object>} 节点数组
 */
function buildRetrievalFlowNodes() {
  var cx = 360;
  var dy = 88;
  return [
    mainNode('q', 'input', cx, 0, '用户问题', '#dbeafe', '#2563eb'),
    customDecisionNode('route', cx - 14, dy, 'route_question\n能力开关'),
    chainNode('retrieve', 40, dy * 2.2, 'retrieve_hybrid ✅\nPG关键词+Neo4j向量+RRF', '#fef3c7', '#d97706'),
    chainNode('grade', 40, dy * 3.2, 'grade_documents ✅\n规则版', '#fef3c7', '#d97706'),
    chainNode('rerank', 40, dy * 4.2, 'rerank ✅ 规则版', '#fef3c7', '#d97706'),
    chainNode('expand', 40, dy * 5.2, 'graph_expand（Phase 3）', '#fef3c7', '#d97706'),
    chainNode('rewrite', 40, dy * 6.4, 'rewrite_query（增强）', '#fef3c7', '#b45309'),
    sideNode('web', 680, dy * 2.8, 'web_search ✅ Tavily\nB直接 / ⑩兜底', '#ffedd5', '#ea580c'),
    mainNode('compact', 'default', cx, dy * 5.8, 'compact_history\n⑭', '#dcfce7', '#16a34a'),
    mainNode('gen', 'default', cx, dy * 6.8, 'generate\n⑮', '#dcfce7', '#16a34a'),
    chainNode('hallu', cx - 86, dy * 7.8, 'grade_hallucination（增强）', '#ede9fe', '#7c3aed'),
    mainNode('done', 'output', cx, dy * 8.8, 'SSE + save', '#dbeafe', '#2563eb')
  ];
}

/**
 * 构建检索工程边
 * @returns {Array<object>} 边数组
 */
function buildRetrievalFlowEdges() {
  return buildRetrievalRouteEdges()
    .concat(buildRetrievalChainEdges())
    .concat(buildRetrievalGuardEdges());
}

/**
 * 构建路由分支边
 * @returns {Array<object>} 边数组
 */
function buildRetrievalRouteEdges() {
  return [
    flowEdge('rq', 'q', 'route', ''),
    branchEdge('ra', 'route', 'retrieve', 'needs_project', BRANCH_A_COLOR, 'left'),
    branchEdge('rb', 'route', 'web', 'needs_web', BRANCH_B_COLOR, 'right'),
    branchEdge('rc', 'route', 'compact', '仅创作', BRANCH_C_COLOR, 'down')
  ];
}

/**
 * 构建检索链与回路边
 * @returns {Array<object>} 边数组
 */
function buildRetrievalChainEdges() {
  return [
    chainEdge('r1', 'retrieve', 'grade', ''),
    chainEdge('r2', 'grade', 'rerank', '相关'),
    chainEdge('r3', 'rerank', 'expand', ''),
    mergeEdge('r4', 'expand', 'compact', '⑬ 检索上下文', 'left'),
    mergeEdge('r5', 'web', 'compact', '⑬ Web 结果', 'right'),
    chainEdge('r6', 'grade', 'rewrite', '不相关'),
    loopEdge('r7', 'rewrite', 'retrieve', 'retry<max', '#b45309'),
    fallbackEdge('r8', 'grade', 'web', '无证据 兜底'),
    flowEdge('r9', 'compact', 'gen', '⑭→⑮')
  ];
}

/**
 * 构建生成护栏边
 * @returns {Array<object>} 边数组
 */
function buildRetrievalGuardEdges() {
  return [
    flowEdge('g1', 'gen', 'hallu', ''),
    flowEdge('g2', 'hallu', 'done', '通过'),
    loopEdge('g3', 'hallu', 'gen', '未 grounded', '#7c3aed')
  ];
}
