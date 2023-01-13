import time
from tools.set_single_instance import Singleton

class Value:
    def __init__(self, value, put_time, expired):
        self.value = value
        self.put_time = put_time
        self.expired = expired

    def __repr__(self):
        return f"value: {self.value}  put_time: {self.put_time}  expired: {self.expired}"

class MemoryCache(metaclass=Singleton):

    def __init__(self):
        self.__cache = {}

    def set(self, k, v, expired=None):
        current_timestamp = int(time.time())  # 获取当前时间戳 10 位 秒级
        value = Value(v, current_timestamp, expired)
        self.__cache[k] = value

    def check(self, k):
        current_timestamp = int(time.time())
        value = self.__cache.get(k, None)
        if value is None:
            return False
        differ = current_timestamp - value.put_time
        if value.expired:
            if differ > value.expired:
                del self.__cache[k]  # 证明缓存失效了，删除键值对
                return False
        return True

    def get(self, k):
        if self.check(k):
            return self.__cache[k].value
        return None

    def list(self):
        return self.__cache

    def __call__(self, *args, **kwargs):
        return self.list()

memory_cache = MemoryCache()


