/**
 * 全流程请求交互图（①–⑲）
 * 职责：定义单次 Chat 请求从 Client 到 SSE 的完整节点与边
 */

/** @type {string} 检索子链节点背景色 */
var RETRIEVE_BG = '#fef3c7';

/** @type {string} 检索子链节点边框色 */
var RETRIEVE_BORDER = '#d97706';

/** @type {string} Web 节点背景色 */
var WEB_BG = '#ffedd5';

/** @type {string} Web 节点边框色 */
var WEB_BORDER = '#ea580c';

/** @type {object} 主请求流程图规格 */
var REQUEST_FLOW_SPEC = {
  mountId: 'architecture-flow-root',
  buildNodes: buildRequestFlowNodes,
  buildEdges: buildRequestFlowEdges
};

/**
 * 构建主请求流程节点
 * @returns {Array<object>} 节点数组
 */
function buildRequestFlowNodes() {
  var y0 = 0;
  var dy = FLOW_STEP_Y;
  return [
    mainNode('client', 'input', FLOW_MAIN_X, y0, '用户 Client', '#dbeafe', '#2563eb'),
    mainNode('api', 'default', FLOW_MAIN_X, y0 + dy, 'Chat API', '#e0e7ff', '#4338ca'),
    mainNode('cfg', 'default', FLOW_MAIN_X, y0 + dy * 2, 'ConfigResolver', '#e0e7ff', '#4338ca'),
    mainNode('load_skill', 'default', FLOW_MAIN_X, y0 + dy * 3, 'load_skill', '#dcfce7', '#16a34a'),
    sideNode('skill', FLOW_RIGHT_X, y0 + dy * 3, 'Skill Registry', '#dcfce7', '#16a34a'),
    mainNode('load_history', 'default', FLOW_MAIN_X, y0 + dy * 4, 'load_history', '#dcfce7', '#16a34a'),
    sideNode('pg_hist', FLOW_PG_SIDE_X, y0 + dy * 4, 'PostgreSQL', '#ffedd5', '#ea580c'),
    decisionNode('route', FLOW_MAIN_X - 14, y0 + dy * 5),
    chainNode('retrieve', FLOW_LEFT_X, y0 + dy * 6.2, '⑨ Hybrid 检索\nNeo4j + PG', RETRIEVE_BG, RETRIEVE_BORDER),
    chainNode('grader', FLOW_LEFT_X, y0 + dy * 7.2, '⑩ Grader 评分\n不相关→重写', RETRIEVE_BG, RETRIEVE_BORDER),
    chainNode('rewrite', FLOW_LEFT_X, y0 + dy * 7.7, '⑩′ rewrite_query', RETRIEVE_BG, '#b45309'),
    chainNode('rerank', FLOW_LEFT_X, y0 + dy * 8.2, '⑪⑫ Rerank\n+ 图扩展', RETRIEVE_BG, RETRIEVE_BORDER),
    sideNode('web_direct', FLOW_RIGHT_X, y0 + dy * 6.2, 'Web Search\nneeds_web', WEB_BG, WEB_BORDER),
    sideNode('web_fallback', FLOW_RIGHT_X, y0 + dy * 7.6, 'Web Search\n⑩ 无证据兜底', WEB_BG, WEB_BORDER),
    mainNode('compact', 'default', FLOW_MAIN_X, y0 + dy * 9.6, 'compact_history\n⑭ 超阈值压缩', '#dcfce7', '#16a34a'),
    mainNode('generate', 'default', FLOW_MAIN_X, y0 + dy * 10.8, 'generate\n⑮ 拼装+流式', '#dcfce7', '#16a34a'),
    sideNode('provider', FLOW_RIGHT_X, y0 + dy * 10.8, 'Provider Registry\n⑯', '#ede9fe', '#7c3aed'),
    mainNode('sse', 'default', FLOW_MAIN_X, y0 + dy * 12, 'FastAPI SSE\n⑰⑱', '#e0e7ff', '#4338ca'),
    mainNode('save', 'default', FLOW_MAIN_X, y0 + dy * 13.2, 'save_messages\n⑲', '#dcfce7', '#16a34a'),
    sideNode('pg_save', FLOW_PG_SIDE_X, y0 + dy * 13.2, 'PostgreSQL', '#ffedd5', '#ea580c'),
    mainNode('client_end', 'output', FLOW_MAIN_X, y0 + dy * 14.4, 'SSE 响应结束', '#dbeafe', '#2563eb')
  ];
}

/**
 * 构建主请求流程边
 * @returns {Array<object>} 边数组
 */
function buildRequestFlowEdges() {
  return buildRequestMainEdges()
    .concat(buildRequestRouteEdges())
    .concat(buildRequestRetrieveEdges())
    .concat(buildRequestMergeEdges());
}

/**
 * 构建主链与 PG 读写边
 * @returns {Array<object>} 边数组
 */
function buildRequestMainEdges() {
  return [
    flowEdge('e01', 'client', 'api', '① POST 发送问题'),
    flowEdge('e02', 'api', 'cfg', '② 解析 profile'),
    flowEdge('e03', 'cfg', 'load_skill', '③ 启动 LangGraph'),
    sideEdge('e04', 'load_skill', 'skill', '④ 匹配并注入 Skill', 'right'),
    flowEdge('e05', 'load_skill', 'load_history', '⑤ 下一节点 load_history'),
    pgSideEdge('e06', 'load_history', 'pg_hist', '⑥ 读取 PG 历史'),
    flowEdge('e07', 'load_history', 'route', '⑦ 进入路由判断'),
    flowEdge('e15', 'compact', 'generate', '⑭→⑮ 进入生成'),
    sideEdge('e16', 'generate', 'provider', '⑯ 流式 LLM', 'right'),
    flowEdge('e17', 'generate', 'sse', '⑰ astream→SSE'),
    flowEdge('e18', 'sse', 'client_end', '⑱ 推送客户端'),
    flowEdge('e19', 'sse', 'save', '⑲ 持久化消息'),
    pgSideEdge('e19b', 'save', 'pg_save', '⑲ 写入 PG')
  ];
}

/**
 * 构建路由三分支边
 * @returns {Array<object>} 边数组
 */
function buildRequestRouteEdges() {
  return [
    branchEdge('e08a', 'route', 'retrieve', 'needs_project→⑨', BRANCH_A_COLOR, 'left'),
    branchEdge('e08b', 'route', 'web_direct', 'needs_web→Web', BRANCH_B_COLOR, 'right'),
    branchEdge('e08c', 'route', 'compact', '仅创作→compact', BRANCH_C_COLOR, 'down')
  ];
}

/**
 * 构建检索子链与兜底边
 * @returns {Array<object>} 边数组
 */
function buildRequestRetrieveEdges() {
  return [
    chainEdge('e09', 'retrieve', 'grader', '⑨ 召回+RRF'),
    chainEdge('e10a', 'grader', 'rerank', '有相关→⑪'),
    chainEdge('e10c', 'grader', 'rewrite', '不相关→⑩′'),
    loopEdge('e10d', 'rewrite', 'retrieve', 'retry<max', '#b45309'),
    fallbackEdge('e10b', 'grader', 'web_fallback', '无证据→兜底Web')
  ];
}

/**
 * 构建三路汇合 compact 边
 * @returns {Array<object>} 边数组
 */
function buildRequestMergeEdges() {
  return [
    mergeEdge('e13a', 'rerank', 'compact', '⑬ 带上检索结果', 'left'),
    mergeEdge('e13b', 'web_direct', 'compact', '⑬ 带上 Web 结果', 'right'),
    mergeEdge('e13c', 'web_fallback', 'compact', '⑬ 带上兜底结果', 'right')
  ];
}
