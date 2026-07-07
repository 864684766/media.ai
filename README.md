# lanmo

基于 FastAPI 构建的项目，使用 Poetry 进行包管理。

## 环境要求

- Python >= 3.10
- Poetry >= 2.0

## 安装

```bash
# 创建虚拟环境并安装依赖
poetry install

# 复制环境变量文件
cp .env.example .env
```

## 运行

```bash
# 推荐：启动开发服务器（带热重载）
poetry run python -m app.run

# 或使用 uvicorn 直接启动
poetry run uvicorn app.application:app --reload --host 0.0.0.0 --port 8000

# 或使用命令行脚本
poetry run lanmo
```

## 入口文件说明

| 文件 | 职责 |
|------|------|
| `app/application.py` | 定义 FastAPI 应用对象 `app`，供 uvicorn 加载 |
| `app/run.py` | 启动 uvicorn 服务器，日常开发从这里运行 |

### PyCharm 运行配置

1. **解释器**：Settings → Project → Python Interpreter → 选择 `.venv\Scripts\python.exe`
2. **运行配置**：右上角 **Edit Configurations...**
   - **Script path**：`app/run.py`（不要选 `application.py` 或已删除的 `main.py`）
   - **Working directory**：项目根目录（`E:\test\lanmo`）
   - **Python interpreter**：`.venv\Scripts\python.exe`
3. **修改代码后**：先点 **Stop** 再 **Run**，调试模式下热重载可能不生效
4. **接口未更新时**：确认旧进程已停止（8000 端口无占用），浏览器 **Ctrl+F5** 强制刷新 `/docs`

## 项目结构

```
lanmo/
├── app/
│   ├── api/                # 路由层
│   ├── core/               # 核心配置
│   ├── models/             # 数据模型
│   ├── schemas/            # 数据校验
│   ├── services/           # 业务服务层
│   ├── utils/              # 工具方法
│   ├── application.py      # FastAPI 应用定义
│   └── run.py              # 服务器启动入口
├── tests/
├── pyproject.toml
└── README.md
```

## 文档

- 架构设计文档（**浏览器打开**）: [docs/ARCHITECTURE.html](docs/ARCHITECTURE.html) — 全部流程图为 Vue Flow（可缩放、可拖拽节点），含 API/State 数据格式示例

在资源管理器中双击 `docs/ARCHITECTURE.html`，或用浏览器直接打开该文件即可阅读（Vue Flow 需联网加载 CDN）。

启动后访问：

- API 文档: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 文档维护约定

每次开发完成后，须对照代码同步更新相关文档：

- **删除**：已废弃功能、已删除接口/文件的描述
- **更新**：路径、命令、参数、流程等与代码不一致的内容
- **添加**：新功能、新接口、新配置缺失的说明
- **避免冗余**：不重复描述，保持文档与代码一致

项目规则详见 [`.cursor/rules/doc-sync.mdc`](.cursor/rules/doc-sync.mdc)。

## 路由注册约定

`app/api/` 下的模块会自动扫描并注册，**无需手动修改 `router.py`**。

新增接口模块步骤：

1. 在 `app/api/` 下新建文件（如 `user.py`）
2. 在文件中定义 `router = APIRouter(...)` 并编写端点
3. 重启服务即可，路由会自动挂载

以下文件不参与扫描：`router.py`、`router_loader.py`、`deps.py`。

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/chat` | 返回简单字符串应答 |
