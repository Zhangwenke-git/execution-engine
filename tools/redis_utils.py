import redis
import traceback
from urllib.parse import urlparse, parse_qs
from retry import retry
from tools.config_loader import conf
from tools.logger import logger
from tools.set_single_instance import Singleton


class RedisConnect(metaclass=Singleton):

    def __init__(self,host=None,port=6379,db=0, **kwargs):

        if host is None:
            host = conf.get("redis.host")
            port = int(conf.get("redis.port"))
            db = int(conf.get("redis.db"))
        self.redis_url = f'redis://{host}:{port}/' \
                         f'{db}'
        try:
            self._conn = self.url_connect(**kwargs)
        except Exception:
            logger.error(f"fail to connect redis,due to error:{traceback.format_exc()}")
        else:
            if self._conn is not None:
                logger.info(f"success to connect redis by url: {self.redis_url}")

    def url_connect(self, **kwargs):
        url_options = dict()
        url = urlparse(self.redis_url)
        for name, value in iter(parse_qs(url.query).items()):
            url_options[name] = value[0]
        if 'db' not in url_options and url.path:
            try:
                url_options['db'] = int(url.path.replace('/', ''))
            except (AttributeError, ValueError):
                pass
        url_options['db'] = int(url_options.get('db', 0))
        url_options['decode_responses'] = True
        _url = url.scheme + '://' + url.netloc
        url_options.update(kwargs)
        return redis.StrictRedis.from_url(_url, **url_options)

    def __getattr__(self, command): #当属性或方法找不到时，执行该操作
        def _(*args, **kwargs):
            return getattr(self._conn, command)(*args, **kwargs)

        return _

    def __enter__(self): #使用with作为上下文时，需要使用该开始函数
        return self._conn

    def __exit__(self, exc_type, exc_value, traceback): #使用with作为上下文时，需要使用该结束函数
        if exc_type is None:
            self._conn.close()
        else:
            return True

    def __del__(self): #销毁对象
        self.close()

    def __call__(self, *args, **kwargs): #当把类当做函数调用时，执行该方法，e.g. obj = RedisConnect(db=0, client_name="default")   x("key")
        return self.get()

@retry(Exception, delay=5, jitter=(1, 3))
def redis_(class_=RedisConnect):
    return class_(db=0, client_name="default")
