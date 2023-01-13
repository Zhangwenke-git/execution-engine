__description__ = '''
    用来封装windows执行dos命令，分两种，一种是收集执行结果，一种是不需要收集执行结果
    '''


import os
import subprocess
from tools.logger import logger


class DocCmd:


    @staticmethod
    def execute_cmd_result(command):
        '''
        执行command命令，并返回执行结果
        :param command: 传入要执行的命令，字符串格式
        :return:返回执行结果，列表格式
        '''
        result_list = []
        result = os.popen(command).readlines()
        for i in result:
            if i == '\n':
                continue
            result_list.append(i.strip('\n'))  # strip() 方法用于移除字符串头尾指定的字符
        return result_list

    @staticmethod
    def execute_bat(batfile):
        """
        :function:执行批处理文件
        :param batfile: .bat路径
        """
        logger.debug(f'Prepare to execute bat file : {batfile}')
        popen_obj = subprocess.Popen(batfile, shell=True, stdout=subprocess.PIPE)
        stdout, stderr = popen_obj.communicate()
        if popen_obj.returncode == 0:
            logger.debug(f'Success to execute bat file!')
        else:
            logger.error(f'Fail to execute bat file!')

    @staticmethod
    def execute_cmd(command):
        '''
        仅执行command命令，不收集执行结果
        :param command: 传入要执行的命令，字符串格式
        '''
        logger.info(f"Launching system order:{command}.")
        os.system(command)
