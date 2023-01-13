import importlib
import inspect
from operator import methodcaller

from tools.logger import logger


class ModuleClassFunc:

    @staticmethod
    def get_class_func_names(class_):
        """
        :function:获取一个类下所有的函数名称
        :param objectName:class的名称
        :return:
        """
        try:
            function_name_list = list(
                filter(lambda m: not m.startswith("__") and not m.endswith("__") and callable(getattr(class_, m)),
                       dir(class_)))
        except Exception as e:
            logger.error(f'Fail to get the function name list below class object: {class_}')
        else:
            return function_name_list

    @staticmethod
    def parse_func_with_string(object, funcName, *args, **kwargs):
        if hasattr(object, funcName):
            try:
                result = getattr(object, funcName)(*args, **kwargs)
            except Exception as e:
                logger.error(f"Fail to execute function: {funcName}, error as follow: {e}!")
            else:
                return result
        else:
            logger.error(f"The class object does not have the function :{funcName}")

    @staticmethod
    def call_str_func(object, funcName, *args, **kwargs):
        if hasattr(object, funcName):
            try:
                result = methodcaller(funcName, *args, **kwargs)(object)
            except Exception as e:
                logger.error(f"Fail to execute function: {funcName}, error as follow: {e}!")
            else:
                return result
        else:
            logger.error(f"The class object does not have the function :{funcName}")

    @staticmethod
    def execute_static_func(objectName, staticFuncName, *args, **kwargs):
        if hasattr(objectName, staticFuncName):
            try:
                result = getattr(objectName, staticFuncName)(*args, **kwargs)
            except Exception as e:
                logger.error(f"Fail to execute function: {staticFuncName}, error as follow: {e}!")
            else:
                return result
        else:
            logger.error(f"The class object does not have the static function :{staticFuncName}")

    @staticmethod
    def parse_module_with_string(module_name):
        return importlib.__import__(module_name)

    @staticmethod
    def get_class_from_module(module_):
        class_list = []
        for name, obj in inspect.getmembers(module_):
            if inspect.isclass(obj):
                class_list.append(obj)
        return class_list
