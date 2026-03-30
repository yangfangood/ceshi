import time

import pytest
import yaml
from pathlib import Path
from api.pet_api import PetAPI
from utils.assert_utils import AssertUtils
from data.data_factory import PetDataFactory
from utils.db_utils import DBUtils
"""
pytest 配置文件
"""

@pytest.fixture(scope="session")
def config():
    """加载配置，整个会话共享"""
    config_path = Path(__file__).parent / "config" / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="session")
def base_url(config):
    """获取 base_url"""
    return config["env"]["base_url"]


@pytest.fixture(scope="session")
def timeout(config):
    """获取超时时间"""
    return config["env"].get("timeout", 10)


@pytest.fixture(scope="class")
def pet_api(base_url, timeout):
    """创建 PetAPI 实例，整个测试类共享"""
    return PetAPI(base_url, timeout)


@pytest.fixture
def assert_utils():
    """断言工具"""
    return AssertUtils()


@pytest.fixture
def pet_data_factory():
    """数据工厂"""
    return PetDataFactory()


@pytest.fixture
def test_pet_id():
    """测试宠物 ID"""
    return int(time.time() * 1000) % 1000000

@pytest.fixture(scope="session")
def db_config(config):
    """获取数据库配置"""
    return config.get("database", {})


@pytest.fixture(scope="class")
def db_utils(db_config):
    """数据库工具实例，整个测试类共享"""
    if not db_config.get("host"):
        pytest.skip("未配置数据库，跳过数据库验证")
    # ⭐ 这里调用 DBUtils 的 __init__ 方法
    utils = DBUtils(db_config)  # ← __init__ 在这里执行
    yield utils # 返回实例给测试用例使用
    utils.close()