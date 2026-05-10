"""数据 Provider 选择与缓存"""

from typing import Optional

from app.config import settings
from app.data.base import ECommerceDataProvider


_provider: Optional[ECommerceDataProvider] = None


def get_data_provider() -> ECommerceDataProvider:
    """获取当前数据 Provider（单例，首次调用时初始化）。"""
    global _provider
    if _provider is not None:
        return _provider

    provider_setting = settings.data_provider

    if not provider_setting or provider_setting == "demo":
        from app.data.demo_provider import DemoDataProvider
        _provider = DemoDataProvider()
    else:
        # 格式: "module.path:ClassName"
        # 示例: "myapp.providers:PostgresDataProvider"
        module_path, class_name = provider_setting.split(":", 1)
        import importlib
        module = importlib.import_module(module_path)
        cls = getattr(module, class_name)
        _provider = cls()

    return _provider


def reset_provider():
    """重置 Provider 缓存（测试用）。"""
    global _provider
    _provider = None
