"""artifact 目录配置读取。"""

from dataclasses import dataclass

from app.core.artifact_constants import DEFAULT_NOVEL_ARTIFACT_DIR
from app.core.config_yaml_loader import load_app_yaml

YAML_KEY_ARTIFACTS = "artifacts"
YAML_KEY_NOVEL_DIR = "novel_dir"


@dataclass(frozen=True)
class ArtifactConfig:
    """artifact 存储配置。"""

    novel_dir: str


def load_artifact_config() -> ArtifactConfig:
    """加载 artifacts 段配置。"""
    root = load_app_yaml()
    block = root.get(YAML_KEY_ARTIFACTS, {})
    novel_dir = DEFAULT_NOVEL_ARTIFACT_DIR
    if isinstance(block, dict):
        novel_dir = str(block.get(YAML_KEY_NOVEL_DIR, novel_dir))
    return ArtifactConfig(novel_dir=novel_dir)
