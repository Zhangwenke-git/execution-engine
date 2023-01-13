import os
import time
import glob
import pytest
import threading
from config.settings import Settings
from lib.ant.Template import AntReport
from lib.core.case_creation import CaseCreate
from tools.color import Color
from tools.doc_cmd import DocCmd
from tools.config_loader import conf
from tools.logger import logger


class PytestExecution(object):

    def __init__(self):
        pass

    def execute(self, exec_id, data_mapping_dict):
        """
        执行的pytest框架的主入口
        @param data_mapping_dict:
        @return:
        """
        is_success, message = False, None
        cond = threading.Condition()

        def launch_pytest(exec_id):
            nonlocal is_success, message
            cond.acquire()
            cond.wait()
            cond.notify()
            if conf("report.flag") == "AllureReport":
                pytest.main(['-v', '--alluredir', Settings.api_report_xml_path])
                Color.green("===============================Execution is over,prepare for allure report===============================")
                DocCmd.execute_bat(Settings.generate_allure_api_report_bat)
            else:
                module_dir = Settings.base_dir + "/testsuites/%s" % exec_id
                api_ant_report_path = os.path.join(Settings.base_dir,"report/ant/%s" % time.strftime("%Y%m%d", time.localtime()))
                if os.path.exists(module_dir):
                    pytest_order = "py.test %s/ --junit-xml=%s/%s/JunitXml.xml --log-cli-level=INFO" % (module_dir, api_ant_report_path, exec_id)
                    DocCmd.execute_cmd(pytest_order)
                    Color.green("=============================Execution is over,prepare for ant report==============================")
                    xml_report_path = os.path.join(api_ant_report_path, exec_id)
                    durations = AntReport.create_ant_report(xml_report_path)
                    Color.cyan("=====================================Report generated success=====================================")
                    message = durations
                    is_success = True
                else:
                    message = "test case create failed"
                    logger.error("pytest execution does not start.")
            cond.release()

        def create_py_file(exec_id):
            cond.acquire()
            cond.notify()
            if len(glob.glob("test_*.py")) == 0:
                creation = CaseCreate()
                is_success = creation(exec_id, data_mapping_dict)
                if is_success:logger.info(f"success to create api test case py file under dir: {exec_id}.")
            cond.wait()
            cond.release()

        t_pytest = threading.Thread(target=launch_pytest, args=(exec_id,))
        t_create = threading.Thread(target=create_py_file, args=(exec_id,))

        for t in [t_pytest, t_create]:
            t.start()

        for t in [t_pytest, t_create]:
            t.join()

        return is_success, message


def pytest_exec(class_=PytestExecution):
    pytest_exe_obj = class_()
    return pytest_exe_obj
