/**
 * 路由决策子图（⑧ 三选一 + 检索顺序 + Web 兜底）
 * 职责：独立展示 route_question 分支逻辑，便于阅读理解
 */

/** @type {object} 路由决策流程图规格 */
var ROUTE_FLOW_SPEC = {
  mountId: 'flow-route-root',
  buildNodes: buildRouteFlowNodes,
  buildEdges: buildRouteFlowEdges,
  minZoom: 0.2
};

/**
 * 构建路由决策节点
 * @returns {Array<object>} 节点数组
 */
function buildRouteFlowNodes() {
  var cx = 320;
  var dy = 100;
  return [
    customDecisionNode('r', cx - 14, 0, 'route_question\n判断问题类型\n三选一'),
    chainNode('n9', 40, dy, '⑨ Hybrid 检索', '#fef3c7', '#d97706'),
    chainNode('n10', 40, dy * 2, '⑩ Grader', '#fef3c7', '#d97706'),
    chainNode('n11', 40, dy * 3, '⑪⑫ Rerank+图扩展', '#fef3c7', '#d97706'),
    sideNode('wd', 620, dy, 'Web\n⑧B 直接', '#ffedd5', '#ea580c'),
    sideNode('wf', 620, dy * 2.2, 'Web\n⑩ 无证据兜底', '#ffedd5', '#ea580c'),
    mainNode('cmp', 'default', cx, dy * 4, 'compact_history', '#dcfce7', '#16a34a')
  ];
}

/**
 * 构建路由决策边
 * @returns {Array<object>} 边数组
 */
function buildRouteFlowEdges() {
  return [
    branchEdge('ra', 'r', 'n9', 'A 查自己库', BRANCH_A_COLOR, 'left'),
    branchEdge('rb', 'r', 'wd', 'B 问实时库外', BRANCH_B_COLOR, 'right'),
    branchEdge('rc', 'r', 'cmp', 'C 闲聊续写', BRANCH_C_COLOR, 'down'),
    chainEdge('e9', 'n9', 'n10', ''),
    chainEdge('e10', 'n10', 'n11', '有相关'),
    fallbackEdge('efb', 'n10', 'wf', '无证据 兜底'),
    mergeEdge('m1', 'n11', 'cmp', '⑬ 检索结果', 'left'),
    mergeEdge('m2', 'wd', 'cmp', '⑬ Web 结果', 'right'),
    mergeEdge('m3', 'wf', 'cmp', '⑬ 兜底结果', 'right')
  ];
}
