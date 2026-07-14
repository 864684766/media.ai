/**
 * Lanmo 架构流程图节点工厂
 * 职责：创建主链、侧向、决策、竖链子流程等各类节点
 */

/**
 * 创建主链节点（上下连接）
 * @param {string} id 节点 id
 * @param {string} type 节点类型
 * @param {number} x X 坐标
 * @param {number} y Y 坐标
 * @param {string} label 显示文本
 * @param {string} bg 背景色
 * @param {string} border 边框色
 * @returns {object} Vue Flow 节点对象
 */
function mainNode(id, type, x, y, label, bg, border) {
  return {
    id: id,
    type: type,
    position: { x: x, y: y },
    sourcePosition: HANDLE_BOTTOM,
    targetPosition: HANDLE_TOP,
    data: { label: label },
    style: nodeStyle(bg, border)
  };
}

/**
 * 创建路由决策节点（能力开关 needs_project / needs_web / needs_creative）
 * @param {string} id 节点 id
 * @param {number} x X 坐标
 * @param {number} y Y 坐标
 * @returns {object} Vue Flow 节点对象
 */
function decisionNode(id, x, y) {
  return {
    id: id,
    position: { x: x, y: y },
    sourcePosition: HANDLE_BOTTOM,
    targetPosition: HANDLE_TOP,
    data: { label: 'route_question\n【能力开关】\nneeds_* 可组合' },
    style: decisionNodeStyle()
  };
}

/**
 * 创建侧节点（左右连接，如 PG、Skill）
 * @param {string} id 节点 id
 * @param {number} x X 坐标
 * @param {number} y Y 坐标
 * @param {string} label 显示文本
 * @param {string} bg 背景色
 * @param {string} border 边框色
 * @returns {object} Vue Flow 节点对象
 */
function sideNode(id, x, y, label, bg, border) {
  return {
    id: id,
    position: { x: x, y: y },
    sourcePosition: HANDLE_RIGHT,
    targetPosition: HANDLE_LEFT,
    data: { label: label },
    style: nodeStyle(bg, border)
  };
}

/**
 * 创建竖链子流程节点（上下连接，用于检索 ⑨⑩⑪⑫）
 * @param {string} id 节点 id
 * @param {number} x X 坐标
 * @param {number} y Y 坐标
 * @param {string} label 显示文本
 * @param {string} bg 背景色
 * @param {string} border 边框色
 * @returns {object} Vue Flow 节点对象
 */
function chainNode(id, x, y, label, bg, border) {
  return {
    id: id,
    position: { x: x, y: y },
    sourcePosition: HANDLE_BOTTOM,
    targetPosition: HANDLE_TOP,
    data: { label: label },
    style: nodeStyle(bg, border)
  };
}

/**
 * 生成普通节点内联样式
 * @param {string} bg 背景色
 * @param {string} border 边框色
 * @returns {object} CSS 样式对象
 */
function nodeStyle(bg, border) {
  return {
    background: bg,
    border: '2px solid ' + border,
    borderRadius: '8px',
    padding: '10px 14px',
    fontSize: '12px',
    lineHeight: '1.45',
    width: '172px',
    minHeight: '44px',
    textAlign: 'center',
    whiteSpace: 'pre-line',
    wordBreak: 'keep-all'
  };
}

/**
 * 创建横向流程节点（左进右出，用于 LR 布局）
 * @param {string} id 节点 id
 * @param {number} x X 坐标
 * @param {number} y Y 坐标
 * @param {string} label 显示文本
 * @param {string} bg 背景色
 * @param {string} border 边框色
 * @returns {object} Vue Flow 节点对象
 */
function horizNode(id, x, y, label, bg, border) {
  return {
    id: id,
    position: { x: x, y: y },
    sourcePosition: HANDLE_RIGHT,
    targetPosition: HANDLE_LEFT,
    data: { label: label },
    style: nodeStyle(bg, border)
  };
}

/**
 * 创建数据库/storage 节点（横向，强调存储角色）
 * @param {string} id 节点 id
 * @param {number} x X 坐标
 * @param {number} y Y 坐标
 * @param {string} label 显示文本
 * @returns {object} Vue Flow 节点对象
 */
function dbNode(id, x, y, label) {
  return horizNode(id, x, y, label, '#ffedd5', '#ea580c');
}

/**
 * 创建自定义文案的决策节点
 * @param {string} id 节点 id
 * @param {number} x X 坐标
 * @param {number} y Y 坐标
 * @param {string} label 显示文本
 * @returns {object} Vue Flow 节点对象
 */
function customDecisionNode(id, x, y, label) {
  return {
    id: id,
    position: { x: x, y: y },
    sourcePosition: HANDLE_BOTTOM,
    targetPosition: HANDLE_TOP,
    data: { label: label },
    style: decisionNodeStyle()
  };
}

/**
 * 生成决策节点内联样式
 * @returns {object} CSS 样式对象
 */
function decisionNodeStyle() {
  return {
    background: '#fff7ed',
    border: '3px solid #ea580c',
    borderRadius: '10px',
    padding: '12px 14px',
    fontSize: '12px',
    lineHeight: '1.5',
    width: '200px',
    minHeight: '72px',
    textAlign: 'center',
    whiteSpace: 'pre-line',
    fontWeight: '600'
  };
}
