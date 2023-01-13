import json
import re

from lib.busyness.BaseFunSet import BaicSet
from tools.logger import logger


class FormatParam(object):

    def _call(self, func_dict: dict):
        """
        :function:根据函数名称，在BaicSet找到对应函，传入tuple参数，并返回函数直接结果
        :param func_dict: 仅含有一个键值对{'instn21': ('22', 'HangZhou')}
        :return: 函数执行的结果
        """
        BaicSetObj = BaicSet()
        key, val = sorted(func_dict.items())[0]  # 经排序后获取第一个键值对
        logger.debug(f'Prepare to call function :[{key}] and parameter is :[{val}]')
        result_ = None
        try:
            result_ = getattr(BaicSetObj, key)(*val)
        except AttributeError:
            logger.error(f"Function :[{key}] not found in object!")
        except TypeError:
            logger.error(f"The parameter *args not found in function :[{key}]!")
        finally:
            return result_

    def _character(self, string: str):
        """
        :function:删除字符串中的特殊字符
        :param string:
        :return:
        """
        character = ['$', '{', '}']
        for char_ in character:
            string = string.replace(char_, '')
        return string

    # def find_all(string:str,pattern=r'\$\{(.+?)\}'): #匹配出${current}中的current字符串
    def _find_all(self, string: str, pattern=r'\$\{.+?>'):
        """
        :function:匹配函数名称和函数参数
        :param string:
        :param pattern:
        :return:like this: [{'instn21': ('11', '12')}, {'current': ('',)}]
        """
        comment = re.compile(pattern, re.DOTALL)
        result_list = comment.findall(string)
        result_list = list(map(self._character, result_list))
        func_dict_list = []
        for fun in result_list:
            func_dict = {}
            fun_list = fun.split("|")  # 将函数名称和函数参数分离开
            try:
                func_dict[fun_list[0]] = fun_list[1]
            except IndexError:
                raise NameError(f"The separative sign '|' in function string: [{fun_list[0]}] not found!")
            func_dict = {k: tuple(v.replace('<', '').replace('>', '').split(',')) for k, v in
                         func_dict.items()}  # 处理参数的中特殊字符，并转换成tuple格式
            func_dict_list.append(func_dict)
        return func_dict_list

    def _func_map(self, dict_: dict):
        """
        :function:将函数名和函数返回结果组成dict并返回
        :param dict_:
        :return:{'instn21': '1112', 'current': '2020-11-20 11:08:57'}
        """
        json_string = json.dumps(dict_)
        function_str_list = self._find_all(json_string)
        func_result_list = list(map(self._call, function_str_list))  # 函数调用的结果列表
        function_name_list = [sorted(func_dict.items())[0][0] for func_dict in function_str_list]
        key_value = dict(zip(function_name_list, func_result_list))
        return key_value

    def format(self, dict_: dict):
        """
        :function:将模板中的数据进行格式化，将函数调用的结果回写到模板中的dict中
        :param dict_:
        :return: dict类型
        """
        from string import Template
        code = Template(json.dumps(dict_))
        string = code.substitute(self._func_map(dict_))
        string = re.sub(r"\|<.*?>", "", string)  # 去除模板中的参数,<>里的参数
        data = json.loads(string)
        return data
