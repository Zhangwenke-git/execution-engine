import os
import time
import shutil
from config.settings import Settings
from tools.logger import logger
from tools.redis_utils import redis_

redis = redis_()


class Cleaner:

    @staticmethod
    def clean_module_file():
        """
        清除多余的测试py文件
        """
        try:
            suit_file_list = os.listdir(Settings.suit_dir)
            for f in suit_file_list:
                filepath = os.path.join(Settings.suit_dir, f)
                if os.path.isfile(filepath):
                    ...
                elif os.path.isdir(filepath):
                    shutil.rmtree(filepath, True)
        except Exception:
            logger.error('fail to remove api module files.')
        else:
            logger.debug(f'remove api module files successfully')

    @staticmethod
    def clean_report_file():
        """
        清除多余的测试报告
        """
        api_ant_report_path = os.path.join(Settings.base_dir,
                                           "report/ant/%s" % time.strftime("%Y%m%d", time.localtime()))
        try:
            report_list = os.listdir(api_ant_report_path)
            for f in report_list:
                filepath = os.path.join(api_ant_report_path, f)
                if os.path.isfile(filepath):
                    ...
                elif os.path.isdir(filepath):
                    shutil.rmtree(filepath, True)
        except Exception:
            logger.error('fail to remove api report files.')
        else:
            logger.debug(f'remove api report files successfully')

    @staticmethod
    def clear_template_file():
        """
        清除测试模板.json文件
        """
        delete_files = []
        completed_exec_ids = redis.lrange("completed_exec_ids", 0, -1)
        completed_exec_ids =  [completed_exec_id[5:] for completed_exec_id in completed_exec_ids]

        def process_file(file):
            if 'HEART_BEAT' not in file:
                return file.split("_EXEC_")[1][:-5]
        try:
            templates = os.path.join(Settings.base_dir, 'templates')
            for root, dirs, files in os.walk(templates):
                for file in files:
                    if file.endswith(".json") and "HEART_BEAT" not in file and process_file(file) in completed_exec_ids:
                        delete_file = os.path.join(root, file)
                        delete_files.append(delete_file)
                        os.remove(delete_file)
        except Exception:
            logger.error('fail to remove API test template json file.')
        else:
            logger.debug(f'remove api case template json files successfully')
