import json
import pytest
from tools.init_config import AllureEnvInitializer
from config.settings import Settings
from tools.config_loader import conf
from lib.core.formate_parm import JsonTemplateReader
from lib.core.cleaner import Cleaner
from tools.redis_utils import redis_
from tools.ftp import _ftp

ftp = _ftp()
redis = redis_()

@pytest.fixture(scope="function")
def json_template(request):
    """
    :function:自动读取json模板
    :param request:
    :return:
    """

    def read_template_by_test_name(**kwargs):
        render_message = JsonTemplateReader().get_data(request.function.__name__, **kwargs)
        return render_message

    return read_template_by_test_name


@pytest.fixture(scope="session", autouse=True)
def init_conf():
    """
    :function:初始化环境信息，生成xml文件，在allure报告中显示
    """
    if conf("report.flag") == "AllureReport":AllureEnvInitializer().init(Settings.api_env_path)


def pytest_sessionstart(session):
    """
    :function:开始前创建生成allure html的bat命令文件，等初始化信息
    :param session:
    """
    if conf("report.flag") == "AllureReport":
        string = r"""
cd /d %~dp0
allure generate {base_dir}\report\allure\xml -o {base_dir}\report\allure\html --clean
        """.format(base_dir=Settings.base_dir)
        ftp.create_bat_file(string, Settings.generate_allure_api_report_bat)


def pytest_sessionfinish(session):
    """
    :function:测试结束后，添加结尾信息，例如生成测试报告，删除一些报告信息
    :param session:
    """
    Cleaner.clear_template_file()



@pytest.fixture(scope="function", autouse=True)
def add_extra_property(record_property, caplog):
    attributes = json.loads(redis.get("attributes"))
    for k, v in attributes.items():
        record_property(k, v)
