/**
 * PG → Neo4j 单向同步流程图（第 4 章）
 * 职责：展示 Source of Truth 与派生索引关系
 */

/** @type {object} 数据同步流程图规格 */
var SYNC_FLOW_SPEC = {
  mountId: 'flow-sync-root',
  buildNodes: buildSyncFlowNodes,
  buildEdges: buildSyncFlowEdges,
  minZoom: 0.25
};

/**
 * 构建 PG 同步节点
 * @returns {Array<object>} 节点数组
 */
function buildSyncFlowNodes() {
  var y = 80;
  return [
    dbNode('pg', 20, y, 'PostgreSQL\nSource of Truth'),
    horizNode('ingest', 280, y, 'Ingestion 流水线\n（未来接入）', '#e0e7ff', '#4338ca'),
    dbNode('neo', 560, y, 'Neo4j\n派生索引 可重建')
  ];
}

/**
 * 构建 PG 同步边
 * @returns {Array<object>} 边数组
 */
function buildSyncFlowEdges() {
  return [
    horizEdge('s1', 'pg', 'ingest', '原始文档/元数据'),
    horizEdge('s2', 'ingest', 'neo', 'chunk/entity/embedding')
  ];
}
