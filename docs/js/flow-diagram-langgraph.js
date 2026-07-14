/**
 * LangGraph 节点编排流程图（第 9 章）
 * 职责：横向展示状态机节点顺序与三分支汇合
 */

/** @type {object} LangGraph 流程图规格 */
var LANGGRAPH_FLOW_SPEC = {
  mountId: 'flow-langgraph-root',
  buildNodes: buildLanggraphFlowNodes,
  buildEdges: buildLanggraphFlowEdges,
  minZoom: 0.2
};

/**
 * 构建 LangGraph 节点
 * @returns {Array<object>} 节点数组
 */
function buildLanggraphFlowNodes() {
  var y = 120;
  var dx = 200;
  return [
    horizNode('start', 0, y, '开始', '#dbeafe', '#2563eb'),
    horizNode('skill', dx, y, 'load_skill', '#dcfce7', '#16a34a'),
    horizNode('hist', dx * 2, y, 'load_history', '#dcfce7', '#16a34a'),
    customDecisionNode('route', dx * 3 - 14, y - 30, 'route_question\n能力开关'),
    horizNode('retrieve', dx * 3, y + 120, 'retrieve_context\nHybrid+RRF+Grader', '#fef3c7', '#d97706'),
    horizNode('web', dx * 4, y + 120, 'Web 兜底\n(no_evidence 时)', '#ffedd5', '#ea580c'),
    horizNode('compact', dx * 4, y, 'compact_history', '#dcfce7', '#16a34a'),
    horizNode('generate', dx * 5, y, 'generate', '#dcfce7', '#16a34a'),
    horizNode('save', dx * 6, y, 'save_messages', '#dcfce7', '#16a34a'),
    horizNode('end', dx * 7, y, '结束', '#dbeafe', '#2563eb')
  ];
}

/**
 * 构建 LangGraph 边
 * @returns {Array<object>} 边数组
 */
function buildLanggraphFlowEdges() {
  return [
    horizEdge('l1', 'start', 'skill', '① 进入图'),
    horizEdge('l2', 'skill', 'hist', '② 加载 Skill'),
    horizEdge('l3', 'hist', 'route', '③ 读 PG 历史'),
    branchEdge('l4a', 'route', 'retrieve', 'needs_project 或 needs_web', BRANCH_A_COLOR, 'down'),
    branchEdge('l4b', 'retrieve', 'web', 'Grader 判无证据', BRANCH_B_COLOR, 'right'),
    branchEdge('l4c', 'route', 'compact', '仅创作（skip_retrieve）', BRANCH_C_COLOR, 'right'),
    mergeEdge('l5a', 'retrieve', 'compact', '⑤ 证据写入 state.retrieval', 'right'),
    mergeEdge('l5b', 'web', 'compact', '⑤ Web 结果并入', 'left'),
    horizEdge('l6', 'compact', 'generate', '⑥ 压缩后进生成'),
    horizEdge('l7', 'generate', 'save', '⑦ 流式完成写 PG'),
    horizEdge('l8', 'save', 'end', '⑧ 结束（SSE 在 API 层）')
  ];
}
