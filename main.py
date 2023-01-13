import nacos
import traceback
import threading
from tools.config_loader import conf
from testsuites.server import server
from http_server import httpserver
from tools.logger import logger


httpserver_t = threading.Thread(target=httpserver,args=())
server_t = threading.Thread(target=server,args=())

def nacos_register():
    try:
        client = nacos.NacosClient(conf.SERVER_ADDRESS, namespace=conf.NAMESPACE)
        response = client.add_naming_instance(service_name=conf.DATA_ID, ip=conf("local.host.ip"),
                                              port=int(conf("server.port")), ephemeral=False,enable=True,
                                              healthy=True,cluster_name=None,weight=1.0,metadata=None)

    except Exception:
        logger.error(f"fail to register nacos server: {traceback.format_exc()}")
    else:
        if response is True:
            logger.info(f"success to register service `{conf.DATA_ID}` to nacos")
        else:
            logger.error(f"fail to register service `{conf.DATA_ID}` to nacos")


if __name__ == "__main__":
    nacos_register()
    try:
        server_t.start()
    except Exception:
        raise
    else:
        httpserver_t.start()
