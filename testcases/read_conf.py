import yaml
from pathlib import Path
from typing import Dict, Any


class ConfigLoader:
    """配置加载器"""

    def __init__(self, config_path: str = None):
        """
        初始化配置加载器
        :param config_path: 配置文件路径，默认为当前目录下的 config.yaml
        """
        if config_path is None:
            # 使用当前文件所在目录下的 config.yaml
            self.config_path = Path(__file__).parent / "config.yaml"
        else:
            self.config_path = Path(config_path)

        self.config = None

    def load(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"YAML 解析失败: {e}")

        self._validate()
        return self.config

    def _validate(self):
        """验证配置完整性"""
        required_keys = ["env", "base_url"]
        for key in required_keys:
            if key not in self.config.get("env", {}):
                raise ValueError(f"配置缺少必要字段: env.{key}")

    def get(self, key: str, default=None):
        """获取配置值"""
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value


# 使用
config_loader = ConfigLoader()
config = config_loader.load()
base_url = config_loader.get("env.base_url")
print(f"base_url: {base_url}")