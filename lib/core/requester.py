import json
import requests
import traceback
from tools.logger import logger


def request_(method, url, headers=None, params=None, data=None, files=None):
    """
    封装的request请求
    @param method:
    @param url:
    @param headers:
    @param params:
    @param data:
    @param files:
    @return:
    """
    try:
        if method.lower() == "post" and params is not None and data is None:
            raise ValueError("please check input parameter and make sure data is needed if you request with POST.")
        global response
        if params and not data:
            if isinstance(params, dict):
                response = requests.request(method, url, params=params, headers=headers)  # get请求
                logger.debug(f"""\nprint response\n:
                {json.dumps(response.json(), indent=4, ensure_ascii=False)}            
                            """)
                return response.json()
            else:
                logger.error("params should be dict type.")
        elif not params:
            if files:
                response = requests.post(url, data, headers=headers, files=files)  # 文件上传
            elif files and data:
                response = requests.request(method, url, json=data, headers=headers, files=files)  # data和文件上传
            elif not files and data:
                response = requests.request(method, url, json=data, headers=headers)  # header为application/json时使用json=data
            else:
                response = requests.request(method, url, headers=headers)
            logger.info(f"\nprint response\n{json.dumps(response.json(), indent=4, ensure_ascii=False)}")
            return response.json()
        else:
            logger.error("request maybe is wrong.")
    except Exception:
        logger.error(f"request error:{traceback.format_exc()}")

