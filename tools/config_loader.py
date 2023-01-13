import os
import traceback
import warnings
from cacheout import Cache
import nacos
import yaml
from config.settings import Settings
from tools.set_single_instance import Singleton

import socket
def extract_ip():
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        st.connect(('10.255.255.255', 1))
        IP = st.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        st.close()
    return IP

cache = Cache()

class NacosConfig(metaclass=Singleton):

    def __init__(self, SERVER_ADDRESS, DATA_ID, NAMESPACE, GROUP):
        self.SERVER_ADDRESS = SERVER_ADDRESS
        self.NAMESPACE = NAMESPACE
        self.DATA_ID = DATA_ID
        self.GROUP = GROUP

    def _merge_data(self, dict1, dict2):
        """
        使用 dict2 和 dict1 合成一个新的字典。
        对于 dict2 和 dict1 都有的 key，都有值得话取第二组，如果dict2为None，则用dict1，否则用dict2。
        """
        if isinstance(dict1, dict) and isinstance(dict2, dict):
            new_dict = {}
            d2_keys = list(dict2.keys())
            for d1k in dict1.keys():
                if d1k in d2_keys:
                    d2_keys.remove(d1k)
                    new_dict[d1k] = self._merge_data(dict1.get(d1k), dict2.get(d1k))
                else:
                    new_dict[d1k] = dict1.get(d1k)
            for d2k in d2_keys:
                new_dict[d2k] = dict2.get(d2k)
            return new_dict
        else:
            if dict2 is None:
                return dict1
            else:
                return dict2

    def _remove(self, string: str):
        if len(string.strip()) != 0 and not string.startswith("#"):
            return string

    def _deal(self, rows: list):
        return {row.split("=")[0].strip(): row.split("=")[1].strip() for row in rows}

    def get_nacos_config(self):
        """读取nacos中的ymal格式的配置文件，并返回为dict"""
        try:
            client = nacos.NacosClient(self.SERVER_ADDRESS, namespace=self.NAMESPACE)  # 连接nacos
            nacos_config = client.get_config(self.DATA_ID, self.GROUP)
        except Exception:
            warnings.warn(f"fail to get configurations from nacos,error as following:{traceback.format_exc()}")
            rows = {}
        else:
            rows = yaml.load(nacos_config, Loader=yaml.FullLoader)
        return rows


class ConfigLoader(NacosConfig, metaclass=Singleton):

    def __init__(self, SERVER_ADDRESS, DATA_ID, NAMESPACE, GROUP):
        super(ConfigLoader, self).__init__(SERVER_ADDRESS, DATA_ID, NAMESPACE, GROUP)
        self.conf = self.load_conf()
        self.details = {}

    def _read_text_config(self):
        with open(Settings.config_file_path, 'r', encoding='utf-8') as f:
            rows = list(filter(self._remove, f.readlines()))
            return self._deal(rows)

    def parse_yaml_config(self):
        with open(Settings.config_file_path, 'r', encoding='utf-8') as f:
            return yaml.load(f,Loader=yaml.FullLoader)



    def load_conf(self):
        dict1 = self.parse_yaml_config()
        dict2 = self.get_nacos_config()
        data = self._merge_data(dict1, dict2)
        data.update({"local.host.ip":extract_ip()})
        self.details = data

        try:
            for k, v in data.items():
                cache.set(k, v)
        except Exception:
            warnings.warn(f"fail to load configurations to cache,error as following:{traceback.format_exc()}")
        else:
            return cache

    def __getattr__(self, command):
        def _(*args, **kwargs):
            if hasattr(self.conf, command):
                return getattr(self.conf, command)(*args, **kwargs)
            else:
                raise AttributeError

        return _

    def __call__(self, *args, **kwargs):
        return self.get(*args, **kwargs)



try:
    SERVER_ADDRESS = os.environ["SERVER_ADDRESS"]
    if SERVER_ADDRESS is None:
        raise ValueError
except KeyError:
    raise

try:
    DATA_ID = os.environ["DATA_ID"]
    if DATA_ID is None:
        raise ValueError
except KeyError:
    DATA_ID = "execution-engine"

try:
    NAMESPACE = os.environ["NAMESPACE"]
except KeyError:
    NAMESPACE=None

try:
    GROUP = os.environ["GROUP"]
except Exception:
    GROUP = "DEFAULT_GROUP"

conf = ConfigLoader(SERVER_ADDRESS,DATA_ID,NAMESPACE,GROUP)
