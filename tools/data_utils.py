import random
from itertools import product

from tools.logger import logger


class DataUtil:

    @staticmethod
    def calculate_percentage(first_num, second_num):
        if second_num <= 0:
            return '0%'
        format = '{:.0%}'
        return format.format(first_num / second_num)

    @staticmethod
    def format_num(self, num, precision=4):
        """
        :function:float数据类型进行设置精度
        :param num:
        :param precision:
        :return:
        """
        try:
            format = "{:.%sf}" % int(precision)
            return format.format(float(num))
        except Exception as e:
            logger.error(f"Fail to format {num},error as follow {e}")
            return num

    @classmethod
    def get_random_float(cls, first_num, second_num, precision):
        try:
            num = random.uniform(float(first_num), float(second_num))
            num = cls.format_num(num, precision)
            logger.debug(f"The random num is {num},and the limit is [{first_num, second_num}]")
            return num
        except Exception as e:
            logger.error(f"Fail to get the random num between {first_num} and {second_num},error as follow {e}")
            return None

    @staticmethod
    def get_random_int(first_num, second_num):
        try:
            num = random.randint(int(first_num), int(second_num))
            logger.debug(f"The random num is {num},and the limit is [{first_num, second_num}]")
            return num
        except Exception as e:
            logger.error(f"Fail to get the random num between {first_num} and {second_num},error as follow {e}")
            return None

    @staticmethod
    def splitInteger(num):
        if isinstance(num, int):
            x = random.randint(1, num - 1)
            y = num - x
            return x, y
        else:
            raise NameError('The data type must be an integer!')

    @staticmethod
    def multi_list_combination(list_array):
        from itertools import product
        result_list = []
        for i in product(*list_array):
            result_list.append(i)
        return result_list

    @staticmethod
    def multi_list_pytest(list_array):
        result_list = []
        ids_list = []
        for i in product(*list_array):
            result_list.append(i)
            p = 'Condition:'
            for j in i:
                p = p + "-" + j
            ids_list.append(p)

        logger.info(f"Prepare to execute {len(result_list)} cases in total!")
        return result_list, ids_list

    @staticmethod
    def list_no_repeat(list_: list):
        """
        :function:列表去重
        :param list_:
        :return:
        """
        list_ = sorted(set(list_), key=list_.index)
        return list_
