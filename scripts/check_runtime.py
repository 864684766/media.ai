"""运行环境连通性检查脚本。

【用途】
    手动验证 .env 中的 Provider / PostgreSQL / Neo4j 是否可用。

【运行】
    poetry run python scripts/check_runtime.py

【注意】
    该脚本会真实调用远程服务；不会打印 API Key 或数据库密码。
"""

from app.providers import check_provider_health
from app.storage import check_neo4j_health, check_postgres_health


def main() -> None:
    """执行三项运行时健康检查。"""
    print("== lanmo runtime check ==")
    print(check_provider_health().model_dump())
    print(check_postgres_health().model_dump())
    print(check_neo4j_health().model_dump())


if __name__ == "__main__":
    main()
