/**
 * Lanmo 架构流程图通用挂载器
 * 职责：按 spec 挂载可拖拽 Vue Flow 实例
 */

/**
 * 挂载单个 Vue Flow 流程图
 * @param {object} spec 图规格 { mountId, buildNodes, buildEdges, minZoom, fitPadding }
 * @returns {void}
 */
function mountVueFlowDiagram(spec) {
  var mountEl = document.getElementById(spec.mountId);
  if (!canMountFlow(mountEl)) {
    return;
  }
  var app = Vue.createApp({ setup: createDiagramSetup(spec) });
  try {
    app.mount(mountEl);
  } catch (err) {
    renderFlowError(mountEl, err.message);
  }
}

/**
 * 判断 Vue Flow 依赖与挂载点是否就绪
 * @param {HTMLElement|null} mountEl 挂载 DOM
 * @returns {boolean} 可挂载时为 true
 */
function canMountFlow(mountEl) {
  return Boolean(mountEl && typeof Vue !== 'undefined' && typeof VueFlowCore !== 'undefined');
}

/**
 * 创建单图 Vue setup
 * @param {object} spec 图规格
 * @returns {Function} setup 函数
 */
function createDiagramSetup(spec) {
  var ref = Vue.ref;
  var h = Vue.h;
  var VueFlow = VueFlowCore.VueFlow;
  var Controls = VueFlowControls.Controls;
  var Background = VueFlowBackground.Background;
  return function () {
    var nodes = ref(spec.buildNodes());
    var edges = ref(spec.buildEdges());
    return function () {
      return h(VueFlow, buildDiagramProps(nodes, edges, spec), buildFlowSlots(h, Background, Controls));
    };
  };
}

/**
 * 构建单图 Vue Flow props（节点可拖拽）
 * @param {object} nodes 节点 ref
 * @param {object} edges 边 ref
 * @param {object} spec 图规格
 * @returns {object} props
 */
function buildDiagramProps(nodes, edges, spec) {
  return {
    nodes: nodes.value,
    edges: edges.value,
    minZoom: spec.minZoom || FLOW_MIN_ZOOM,
    maxZoom: FLOW_MAX_ZOOM,
    fitViewOnInit: true,
    nodesDraggable: true,
    nodesConnectable: false,
    elementsSelectable: true,
    defaultEdgeOptions: { type: 'smoothstep', labelShowBg: true, labelBgPadding: [5, 8] },
    'onUpdate:nodes': function (val) { nodes.value = val; },
    'onUpdate:edges': function (val) { edges.value = val; },
    onInit: function (instance) {
      instance.fitView({ padding: spec.fitPadding || FLOW_FIT_PADDING, duration: 300 });
    }
  };
}

/**
 * 构建 Vue Flow 默认插槽
 * @param {Function} h Vue h
 * @param {object} Background Background 组件
 * @param {object} Controls Controls 组件
 * @returns {object} 插槽对象
 */
function buildFlowSlots(h, Background, Controls) {
  return {
    default: function () {
      return [
        h(Background, { patternColor: '#e2e8f0', gap: 18 }),
        h(Controls, { showZoom: true, showFitView: true, showInteractive: false })
      ];
    }
  };
}

/**
 * 渲染流程图加载失败提示
 * @param {HTMLElement} mountEl 挂载 DOM
 * @param {string} message 错误信息
 * @returns {void}
 */
function renderFlowError(mountEl, message) {
  mountEl.innerHTML = '<p style="padding:1rem;color:#b91c1c;">流程图加载失败：' + message + '</p>';
}
