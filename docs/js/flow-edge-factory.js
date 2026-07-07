/**
 * Lanmo 架构流程图边工厂
 * 职责：创建主链、侧向、分支、汇合、兜底虚线等各类连线
 */

/**
 * 创建默认边标签文字样式
 * @returns {object} 标签样式
 */
function labelStyle() {
  return { fill: '#1e293b', fontSize: 10, fontWeight: 600 };
}

/**
 * 创建默认边标签背景样式
 * @returns {object} 标签背景样式
 */
function labelBgStyle() {
  return { fill: '#ffffff', fillOpacity: 0.96, stroke: '#cbd5e1', strokeWidth: 1 };
}

/**
 * 创建 PG 侧向边标签样式（偏左放置，避免被主链节点遮挡）
 * @returns {object} 标签样式
 */
function pgLabelStyle() {
  return { fill: '#1e293b', fontSize: 10, fontWeight: 600, transform: 'translateX(-28px)' };
}

/**
 * 创建边公共字段
 * @param {string} id 边 id
 * @param {string} source 源节点 id
 * @param {string} target 目标节点 id
 * @param {string} label 中文标签
 * @param {object} extra 额外属性（type、style、labelStyle 等）
 * @returns {object} Vue Flow 边对象
 */
function baseEdge(id, source, target, label, extra) {
  var edge = {
    id: id,
    source: source,
    target: target,
    label: label,
    labelStyle: labelStyle(),
    labelBgStyle: labelBgStyle(),
    labelBgPadding: [5, 8],
    labelShowBg: true
  };
  Object.keys(extra).forEach(function (key) {
    edge[key] = extra[key];
  });
  return edge;
}

/**
 * 创建主链纵向边
 * @param {string} id 边 id
 * @param {string} source 源节点 id
 * @param {string} target 目标节点 id
 * @param {string} label 中文标签
 * @returns {object} 边对象
 */
function flowEdge(id, source, target, label) {
  return baseEdge(id, source, target, label, {
    type: 'smoothstep',
    style: { stroke: FLOW_EDGE_COLOR, strokeWidth: 2 }
  });
}

/**
 * 创建侧向交互边（单线表达请求+返回）
 * @param {string} id 边 id
 * @param {string} source 源节点 id
 * @param {string} target 目标节点 id
 * @param {string} label 中文标签
 * @param {string} side 侧向方向 left 或 right
 * @returns {object} 边对象
 */
function sideEdge(id, source, target, label, side) {
  var toLeft = side === 'left';
  return baseEdge(id, source, target, label, {
    type: 'smoothstep',
    sourceHandle: toLeft ? HANDLE_LEFT : HANDLE_RIGHT,
    targetHandle: toLeft ? HANDLE_RIGHT : HANDLE_LEFT,
    style: { stroke: FLOW_EDGE_COLOR, strokeWidth: 1.8 }
  });
}

/**
 * 创建 PG 读写侧向边（标签偏左，避免被主链节点遮挡）
 * @param {string} id 边 id
 * @param {string} source 源节点 id
 * @param {string} target PG 侧节点 id
 * @param {string} label 中文标签
 * @returns {object} 边对象
 */
function pgSideEdge(id, source, target, label) {
  return baseEdge(id, source, target, label, {
    type: 'smoothstep',
    sourceHandle: HANDLE_LEFT,
    targetHandle: HANDLE_RIGHT,
    labelStyle: pgLabelStyle(),
    style: { stroke: FLOW_EDGE_COLOR, strokeWidth: 1.8 }
  });
}

/**
 * 创建路由分支边（三分支互斥，中文条件标签）
 * @param {string} id 边 id
 * @param {string} source 源节点 id
 * @param {string} target 目标节点 id
 * @param {string} label 中文条件
 * @param {string} color 线条颜色
 * @param {string} direction left / right / down
 * @returns {object} 边对象
 */
function branchEdge(id, source, target, label, color, direction) {
  var handles = branchHandleMap();
  var h = handles[direction] || handles.down;
  return baseEdge(id, source, target, label, {
    type: 'smoothstep',
    sourceHandle: h.source,
    targetHandle: h.target,
    style: { stroke: color, strokeWidth: 2.5 }
  });
}

/**
 * 创建检索子链竖向边（⑨→⑩→⑪⑫ 顺序）
 * @param {string} id 边 id
 * @param {string} source 源节点 id
 * @param {string} target 目标节点 id
 * @param {string} label 中文标签
 * @returns {object} 边对象
 */
function chainEdge(id, source, target, label) {
  return baseEdge(id, source, target, label, {
    type: 'smoothstep',
    style: { stroke: BRANCH_A_COLOR, strokeWidth: 2 }
  });
}

/**
 * 创建分支汇合边（侧节点汇入主链 compact）
 * @param {string} id 边 id
 * @param {string} source 源节点 id
 * @param {string} target 目标节点 id
 * @param {string} label 中文标签
 * @param {string} side left 或 right
 * @returns {object} 边对象
 */
function mergeEdge(id, source, target, label, side) {
  var fromLeft = side === 'left';
  return baseEdge(id, source, target, label, {
    type: 'smoothstep',
    sourceHandle: fromLeft ? HANDLE_RIGHT : HANDLE_LEFT,
    targetHandle: fromLeft ? HANDLE_LEFT : HANDLE_RIGHT,
    style: { stroke: FLOW_EDGE_COLOR, strokeWidth: 1.8 }
  });
}

/**
 * 创建 Grader 无证据兜底虚线（⑩ → Web 兜底）
 * @param {string} id 边 id
 * @param {string} source Grader 节点 id
 * @param {string} target Web 兜底节点 id
 * @param {string} label 中文标签
 * @returns {object} 边对象
 */
function fallbackEdge(id, source, target, label) {
  return baseEdge(id, source, target, label, {
    type: 'smoothstep',
    sourceHandle: HANDLE_RIGHT,
    targetHandle: HANDLE_LEFT,
    animated: true,
    style: {
      stroke: FALLBACK_DASH_COLOR,
      strokeWidth: 2.2,
      strokeDasharray: '8 5'
    }
  });
}

/**
 * 创建横向流程边（LR 布局）
 * @param {string} id 边 id
 * @param {string} source 源节点 id
 * @param {string} target 目标节点 id
 * @param {string} label 中文标签
 * @param {string} [color] 线条颜色，默认主链蓝
 * @returns {object} 边对象
 */
function horizEdge(id, source, target, label, color) {
  return baseEdge(id, source, target, label, {
    type: 'smoothstep',
    style: { stroke: color || FLOW_EDGE_COLOR, strokeWidth: 2 }
  });
}

/**
 * 创建回路边（如 rewrite → retrieve）
 * @param {string} id 边 id
 * @param {string} source 源节点 id
 * @param {string} target 目标节点 id
 * @param {string} label 中文标签
 * @param {string} color 线条颜色
 * @returns {object} 边对象
 */
function loopEdge(id, source, target, label, color) {
  return baseEdge(id, source, target, label, {
    type: 'smoothstep',
    sourceHandle: HANDLE_LEFT,
    targetHandle: HANDLE_LEFT,
    style: { stroke: color, strokeWidth: 1.8, strokeDasharray: '6 4' }
  });
}

/**
 * 返回路由分支连接点映射
 * @returns {object} direction → { source, target } 映射
 */
function branchHandleMap() {
  return {
    left: { source: HANDLE_LEFT, target: HANDLE_RIGHT },
    right: { source: HANDLE_RIGHT, target: HANDLE_LEFT },
    down: { source: HANDLE_BOTTOM, target: HANDLE_TOP }
  };
}
