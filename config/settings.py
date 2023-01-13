import os
import sys

class Settings:

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    sys.path.append(base_dir)

    success_flag = 'PASS'

    fail_flag = 'FAIL'

    log_path = os.path.join(base_dir, 'log')

    template_dir = os.path.join(base_dir, 'templates')

    suit_dir = os.path.join(base_dir, 'testsuites')

    api_env_path = os.path.join(base_dir, "report/allure/xml/environment.xml")

    api_report_xml_path = os.path.join(base_dir, "report/allure/xml")

    generate_allure_api_report_bat = os.path.join(base_dir, 'bat/generate_allure_api_report.bat')

    template_file_path = os.path.join(base_dir, 'lib/ant/template')

    config_file_path = os.path.join(base_dir, 'config/config.yaml')
