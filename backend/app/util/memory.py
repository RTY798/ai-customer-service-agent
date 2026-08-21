import uuid
from threading import Lock
from typing import Optional

class ThreadIdCache:
    """
    线程安全的 thread_id 缓存管理器
    功能：根据 userId 生成并缓存 UUID，模拟 Java 中的 ConcurrentHashMap
    """
    def __init__(self):
        self._cache: dict[str, str] = {}
        self._lock = Lock()

    def get_or_create(self, user_id: str) -> str:
        """
        获取或创建 thread_id
        :param user_id: 前端传入的用户标识
        :return: UUID 字符串 (例如: "f47ac10b-58cc-4372-a567-0e02b2c3d479")
        """
        # 统一转为字符串，防止 int 或其它类型导致 JSON 配置报错
        key = str(user_id)

        # 使用双重检查锁（Double-Checked Locking）优化性能
        # 先无锁检查读，绝大多数命中时无需竞争锁
        if key in self._cache:
            return self._cache[key]

        with self._lock:
            # 二次检查，防止在等待锁期间被其他线程创建
            if key not in self._cache:
                # 生成随机 UUID，与 Java 的 UUID.randomUUID() 完全等价
                new_thread_id = str(uuid.uuid4())
                self._cache[key] = new_thread_id
            return self._cache[key]

    def get(self, user_id: str) -> Optional[str]:
        """仅查询，不创建，用于调试"""
        return self._cache.get(str(user_id))

    def clear(self):
        """清空缓存（慎用，通常用于测试）"""
        with self._lock:
            self._cache.clear()


# 创建全局单例对象，供整个项目复用
thread_id_cache = ThreadIdCache()