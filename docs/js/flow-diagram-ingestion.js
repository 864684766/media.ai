/**
 * Ingestion Lite 流水线流程图（第 13 章）
 * 职责：展示 PG → Neo4j 单向写入的切分与 embedding 步骤
 */

/** @type {object} Ingestion 流程图规格 */
var INGESTION_FLOW_SPEC = {
  mountId: 'flow-ingestion-root',
  buildNodes: buildIngestionFlowNodes,
  buildEdges: buildIngestionFlowEdges,
  minZoom: 0.22
};

/**
 * 构建 Ingestion 节点
 * @returns {Array<object>} 节点数组
 */
function buildIngestionFlowNodes() {
  var y = 100;
  var dx = 170;
  return [
    horizNode('upload', 0, y, '上传/导入', '#dbeafe', '#2563eb'),
    horizNode('clean', dx, y, '清洗', '#e0e7ff', '#4338ca'),
    horizNode('split', dx * 2, y, '切分 chunk', '#fef3c7', '#d97706'),
    horizNode('meta', dx * 3, y, '元数据标注', '#fef3c7', '#d97706'),
    horizNode('embed', dx * 4, y, '生成 embedding', '#ede9fe', '#7c3aed'),
    dbNode('pgw', dx * 5, y - 70, '写入 PG\ndocuments'),
    dbNode('neow', dx * 5, y + 70, '写入 Neo4j\n图谱'),
    horizNode('entity', dx * 6, y + 70, '实体/关系抽取\n（可选）', '#f1f5f9', '#64748b')
  ];
}

/**
 * 构建 Ingestion 边
 * @returns {Array<object>} 边数组
 */
function buildIngestionFlowEdges() {
  return [
    horizEdge('i1', 'upload', 'clean', ''),
    horizEdge('i2', 'clean', 'split', ''),
    horizEdge('i3', 'split', 'meta', ''),
    horizEdge('i4', 'meta', 'embed', ''),
    horizEdge('i5', 'embed', 'pgw', '写 PG'),
    horizEdge('i6', 'embed', 'neow', '写 Neo4j'),
    horizEdge('i7', 'neow', 'entity', 'Phase 3 增强')
  ];
}
