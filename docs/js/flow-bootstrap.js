/**
 * Lanmo 架构文档 Vue Flow 启动器
 * 职责：在 DOM 就绪后挂载全部流程图实例
 */

/** @type {Array<object>} 全部流程图规格列表 */
var FLOW_DIAGRAM_REGISTRY = [
  REQUEST_FLOW_SPEC,
  ROUTE_FLOW_SPEC,
  SYNC_FLOW_SPEC,
  RETRIEVAL_FLOW_SPEC,
  LANGGRAPH_FLOW_SPEC,
  MCP_FLOW_SPEC,
  INGESTION_FLOW_SPEC
];

/**
 * 挂载文档内全部 Vue Flow 图
 * @returns {void}
 */
function mountAllFlowDiagrams() {
  FLOW_DIAGRAM_REGISTRY.forEach(function (spec) {
    mountVueFlowDiagram(spec);
  });
}

document.addEventListener('DOMContentLoaded', mountAllFlowDiagrams);
