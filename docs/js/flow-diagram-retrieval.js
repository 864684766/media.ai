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
    customDecisionNode('route', cx - 14, dy, 'route_question\n三选一'),
    chainNode('retrieve', 40, dy * 2.2, 'retrieve_hybrid', '#fef3c7', '#d97706'),
    chainNode('grade', 40, dy * 3.2, 'grade_documents', '#fef3c7', '#d97706'),
    chainNode('rerank', 40, dy * 4.2, 'rerank', '#fef3c7', '#d97706'),
    chainNode('expand', 40, dy * 5.2, 'graph_expand', '#fef3c7', '#d97706'),
    chainNode('rewrite', 40, dy * 6.4, 'rewrite_query', '#fef3c7', '#b45309'),
    sideNode('web', 680, dy * 2.8, 'web_search\nB直接 / ⑩兜底', '#ffedd5', '#ea580c'),
    mainNode('gen', 'default', cx, dy * 6.2, 'generate_with_citations', '#dcfce7', '#16a34a'),
    chainNode('hallu', cx - 86, dy * 7.4, 'grade_hallucination', '#ede9fe', '#7c3aed'),
    mainNode('done', 'output', cx, dy * 8.6, 'return SSE', '#dbeafe', '#2563eb')
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
    branchEdge('ra', 'route', 'retrieve', 'A project', BRANCH_A_COLOR, 'left'),
    branchEdge('rb', 'route', 'web', 'B realtime', BRANCH_B_COLOR, 'right'),
    branchEdge('rc', 'route', 'gen', 'C general', BRANCH_C_COLOR, 'down')
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
    mergeEdge('r4', 'expand', 'gen', '检索上下文', 'left'),
    mergeEdge('r5', 'web', 'gen', 'Web 结果', 'right'),
    chainEdge('r6', 'grade', 'rewrite', '不相关'),
    loopEdge('r7', 'rewrite', 'retrieve', 'retry<max', '#b45309'),
    fallbackEdge('r8', 'grade', 'web', '无证据 兜底')
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
