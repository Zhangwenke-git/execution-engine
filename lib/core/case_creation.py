import json
import os
import traceback
import uuid
from copy import deepcopy
from string import Template
from config.settings import Settings
from tools.logger import logger
from tools.redis_utils import redis_

redis = redis_()


class CaseCreate:

    @classmethod
    def _template_json_create(cls, exec_id, data: list):
        """
        根据入参生成templates目录下的.json模板文件
        @param data:
        """
        is_success = False
        try:
            for template_json in data:
                template_json_copy = deepcopy(template_json)
                del template_json_copy["scenarios"]
                template_json_copy = template_json_copy["casetemplate"]
                if not os.path.exists(Settings.template_dir):os.makedirs(Settings.template_dir)
                template_file = os.path.join(Settings.template_dir,"test_%s_%s.json" % (template_json.get("case"), exec_id))
                with open(template_file, "w", encoding="utf-8") as f:f.write(json.dumps(template_json_copy, indent=4, ensure_ascii=False))
        except Exception:
            logger.error(
                f"fail to create template json file due to missing necessary element error:{traceback.format_exc()}")
        else:
            logger.info(f"create template json file successfully.")
            is_success = True
        finally:
            return is_success

    @classmethod
    def _single_function_create(cls, exec_id, case_info):
        """
        写入test_func测试函数，即测试用例
        @param caseinfo:
        @return:
        """
        code = Template(r'''
    @pytest.mark.parametrize("desc,param,expect", json.loads(redis.get("${scenario_key}")))
    @allure.story("Case:${title}")
    @allure.severity("critical")
    def test_${testfunction}_${exec_id}(self,desc,param,expect,json_template):
        """${description}"""
        with allure.step("step:生成测试数据"):
            param = Asserter.update_param(param)
            param = param if param !='' and param is not None else dict()
            case = json_template(**param)
            allure.attach(json.dumps(case,indent=4,ensure_ascii=False),"配置信息",allure.attachment_type.JSON)
        with allure.step("step:函数调用"):
            data_ = case.get('data')
            data = format_object.format(data_)
            allure.attach(json.dumps(data,indent=4,ensure_ascii=False),"请求入参",allure.attachment_type.JSON)
        with allure.step(f"step:请求url: {case.get('url')}"):
            if case.get('method').upper() in ['POST','PUT']:
                res = request_(method=case.get('method').upper(),url=case.get('url'),headers=case.get('header'), data=data)
            elif case.get('method').upper()=='GET':
                res = request_("GET",url=case.get('url'),headers=case.get('header'), params=data)
            else:
                res = request_(case.get('method').upper(),url=case.get('url'),headers=case.get('header'))
        with allure.step("step:是否数据库对比"):
            dbinfo = dict(url=case["dbinfo_config"],sql=case["sql"]) if case.get("dbinfo_config") and case.get("sql") else None
        with allure.step("step:请求断言"):
            for item in expect:
                assert Asserter.response_assert(item,res)
                assert Asserter.reqeust_param_assert(item,param)
                assert Asserter.db_assert(item,dbinfo)     
    ''')
        scenario_key = "scenarios_%s" % str(uuid.uuid4())
        redis.set(scenario_key, json.dumps(case_info['scenarios'], ensure_ascii=False), ex=30)
        string = code.substitute(testfunction=case_info["case"], exec_id=exec_id, title=case_info["case_title"],
                                 description=case_info["case_description"], scenario_key=scenario_key)
        return string

    @classmethod
    def _single_class_create(cls, case_info):
        """
        写入测试类
        @param case_info:
        @return:
        """
        code = Template(r"""
import json    
import pytest
import allure
from lib.core.requester import request_
from lib.core.formatter import FormatParam
from lib.core.assertion import Asserter
from tools.redis_utils import redis_

redis = redis_()
format_object = FormatParam()

@pytest.mark.API
@allure.feature("Title:${class_title}")
class TestCase_${module}(object):
                """)

        string = code.substitute(module=case_info["module"], class_title=case_info["class_title"])
        return string

    @classmethod
    def create(cls, exec_id, data_mapping_dict):
        """
        生成测试用例文件的主入口
        @param data_mapping_dict:[dict1,dict2,dict3...]
        """
        is_success = False
        assert cls._template_json_create(exec_id, data_mapping_dict), "create template json files failed"
        try:
            def create_case_function(func_map):
                """
                创建module中的function部分，增加lock保证，先写入class再写function
                @param func_map:
                """
                exec_id_dir = os.path.join(Settings.suit_dir, exec_id)
                test_case_file = os.path.join(exec_id_dir, 'test_{}.py'.format(func_map["module"]))
                with open(test_case_file, 'a', encoding='utf-8') as f:f.write(cls._single_function_create(exec_id, func_map))

            def create_case_class(func_map):
                """
                创建module中的class部分
                @param func_map:
                """
                exec_id_dir = os.path.join(Settings.suit_dir, exec_id)
                if not os.path.exists(exec_id_dir):os.makedirs(exec_id_dir)
                test_case_file = os.path.join(exec_id_dir, 'test_{}.py'.format(func_map["module"]))
                with open(test_case_file, 'w', encoding='utf-8') as f:f.write(cls._single_class_create(func_map))

            list(map(create_case_class,data_mapping_dict))
            list(map(create_case_function,data_mapping_dict))
        except Exception:
            logger.error(f"fail to create module file due to error:{traceback.format_exc()}.")
        else:
            is_success = True
        finally:
            return is_success

    def __call__(self, *args, **kwargs):
        return self.create(*args, **kwargs)