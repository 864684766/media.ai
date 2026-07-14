/**
 * Lanmo 架构流程图布局与样式常量
 * 职责：集中管理坐标、颜色、连接点方向等字面量配置
 */

/** @type {string} 主请求流程图挂载点 DOM id */
var FLOW_MOUNT_ID = 'architecture-flow-root';

/** @type {number} 主流程图面板高度（像素） */
var FLOW_PANEL_HEIGHT_TALL = 880;

/** @type {number} 中等流程图面板高度（像素） */
var FLOW_PANEL_HEIGHT_MD = 560;

/** @type {number} 小型流程图面板高度（像素） */
var FLOW_PANEL_HEIGHT_SM = 420;

/** @type {number} Vue Flow 默认最小缩放 */
var FLOW_MIN_ZOOM = 0.12;

/** @type {number} Vue Flow 默认最大缩放 */
var FLOW_MAX_ZOOM = 2;

/** @type {number} fitView 内边距比例 */
var FLOW_FIT_PADDING = 0.14;

/** @type {number} 主流程列 X 坐标 */
var FLOW_MAIN_X = 420;

/** @type {number} 左侧检索子链 X 坐标 */
var FLOW_LEFT_X = 20;

/** @type {number} 右侧 Web 分支 X 坐标 */
var FLOW_RIGHT_X = 900;

/** @type {number} PostgreSQL 侧节点 X（靠左，避免边标签被主链遮挡） */
var FLOW_PG_SIDE_X = 20;

/** @type {number} 节点垂直间距（像素） */
var FLOW_STEP_Y = 96;

/** @type {string} 主链节点默认入边方向 */
var HANDLE_TOP = 'top';

/** @type {string} 主链节点默认出边方向 */
var HANDLE_BOTTOM = 'bottom';

/** @type {string} 侧节点左侧连接点 */
var HANDLE_LEFT = 'left';

/** @type {string} 侧节点右侧连接点 */
var HANDLE_RIGHT = 'right';

/** @type {string} 主链实线颜色 */
var FLOW_EDGE_COLOR = '#2563eb';

/** @type {string} 分支 A 颜色（查自己库） */
var BRANCH_A_COLOR = '#16a34a';

/** @type {string} 分支 B 颜色（实时 Web） */
var BRANCH_B_COLOR = '#ea580c';

/** @type {string} 分支 C 颜色（仅创作，无检索/Web） */
var BRANCH_C_COLOR = '#2563eb';

/** @type {string} 兜底虚线颜色 */
var FALLBACK_DASH_COLOR = '#ea580c';
