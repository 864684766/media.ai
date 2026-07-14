"""配置文件路径解析。

【本文件职责】
    告诉程序 config/app.yaml 在磁盘上的绝对路径。

【为什么用 Path(__file__)】
    无论从哪个目录启动 uvicorn，都能根据当前 .py 文件位置找到项目根。
    例：本文件在 app/core/config_paths.py → 向上两级 → 项目根 → config/app.yaml

【何时调用】
    config_yaml_loader.load_app_yaml() 读取配置前会用到 get_app_yaml_path()。
"""

from pathlib import Path

# 相对项目根的路径片段（只在这里写一次 "config"、"app.yaml"）
CONFIG_DIR_NAME = "config"
APP_YAML_FILENAME = "app.yaml"
# 高级运维可选；仓库默认不包含此文件
OVERRIDE_YAML_FILENAME = "config.override.yaml"


def get_project_root() -> Path:
    """返回项目根目录（含 pyproject.toml 的目录）。

    返回:
        Path: 绝对路径的项目根。
    """
    # app/core/ → app/ → 项目根
    return Path(__file__).resolve().parent.parent.parent


def get_app_yaml_path() -> Path:
    """返回默认运维配置文件路径。

    返回:
        Path: 例如 E:/test/media.ai/config/app.yaml
    """
    return get_project_root() / CONFIG_DIR_NAME / APP_YAML_FILENAME


def get_override_yaml_path() -> Path:
    """返回高级覆盖配置文件路径（可选，默认可能不存在）。

    返回:
        Path: 例如 .../config/config.override.yaml
    """
    return get_project_root() / CONFIG_DIR_NAME / OVERRIDE_YAML_FILENAME
