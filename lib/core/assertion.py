import copy
import json
import traceback

import jsonpath
from tools.logger import logger
from tools.mysql_utils import parse_mysql_dbinfo

"""
data_type = {"字符串": 0, "整型": 1, "Null": 2, "空字符串": 3, "True": 4, "False": 5, "浮点型": 6, "JSON类型": 7, "List类型": 8}
"""

class Asserter:

    @classmethod
    def parser(cls, param: dict):
        """
        数据的类型转换为对应的真正数据类型
        @param param:
        @return:
        """
        param_copy = copy.deepcopy(param)
        type_ = param_copy["type"]
        val = param_copy["val"]
        try:
            if int(type_) == 0:
                param_copy.update(val=str(val))
            elif int(type_) == 1:
                param_copy.update(val=int(val))
            elif int(type_) == 2:
                param_copy.update(val=None)
            elif int(type_) == 3:
                param_copy.update(val="")
            elif int(type_) == 4:
                param_copy.update(val=True)
            elif int(type_) == 5:
                param_copy.update(val=False)
            elif int(type_) == 6:
                param_copy.update(val=float(val))
            elif int(type_) in (7, 8):
                param_copy.update(val=json.loads(val))
            else:
                raise AttributeError("wrong data type.")
        except Exception:
            raise NotImplementedError(f"fail to convert data due to error: {traceback.format_exc()}")
        else:
            return param_copy

    @classmethod
    def update_param(cls, param: list):
        """
        将真正的数据类型组成字典格式
        @param param:
        @return:
        """
        param = map(cls.parser, param)
        return {iter["field"]: iter["val"] for iter in param}

    @classmethod
    def rule_name(cls, mode: int):
        rule = {"Strict": 0, "Include": 1, "Prefix": 2, "Suffix": 3, "Length": 4, "Ignore": 5}
        for k, v in rule.items():
            if int(v) == int(mode):
                return k

    @classmethod
    def response_assert(cls, validator: dict, response: dict) ->bool:
        """
        根据表达式，在dict检索出符合表达式的值
        @param validator:
        {
            "val": "zhang.wenke",
            "mode": 0,
            "type": 0,
            "field": "user_id",
            "expression": "$.user_id",
            "param_field": "username"
        }
        @param pattern: 匹配表达式，例如$.list[3].user_id
        @return: list
        """
        compared_result = True
        if isinstance(validator, dict):
            data = cls.parser(validator)
            pattern = data["expression"]

            logger.debug("assert response value and expected")
            if pattern.startswith("$"):
                expected = data["val"]
                mode = data["mode"]

                actual = jsonpath.jsonpath(response, pattern)
                if actual == False:
                    compared_result = False
                    logger.error(f"not matched by pattern: {pattern},please check the pattern.")
                else:
                    logger.info(
                        f"actual parsed result: `{actual}` by pattern: {pattern} and rule: {cls.rule_name(mode)}.")
                    try:
                        if int(mode) == 0:
                            assert actual[0] == expected, "strict compared failed"
                        elif int(mode) == 1:
                            assert expected in actual[0], "include compared failed"
                        elif int(mode) == 2:
                            assert actual[0].startswith(expected), "prefix compared failed"
                        elif int(mode) == 3:
                            assert actual[0].endswith(expected), "suffix compared failed"
                        elif int(mode) == 4:
                            assert len(actual[0]) == int(expected), "length compared failed"
                        elif int(mode) == 5:
                            compared_result = True
                        else:
                            logger.error(f"not supported mode:{mode},only support {('strict','include','prefix','suffix','Bool','length')}")
                            compared_result = False
                    except AssertionError:
                        logger.error(f"actual result: {actual[0]},but expected result: {expected}")
                        compared_result = False

                return compared_result
            else:
                logger.error("pattern must start with '$' character,please check it.")
                raise AttributeError("pattern must start with '$' character,please check it.")
        else:
            logger.error("data must be dict type if you using the third module named jsonpath.")
            raise AttributeError("only JSON or DICT are supported")

    @classmethod
    def reqeust_param_assert(cls, validator: dict, param: dict):
        """
        对比请求参数和预期结果值
        @validator:
        {
            "val": "zhang.wenke",
            "mode": 0,
            "type": 0,
            "field": "user_id",
            "expression": "$.user_id",
            "param_field": "username"
        }
        @param:{'password': 'aaaa1111!', 'username': 'admin'}
        """
        flag = True
        param_field = validator.get("param_field")
        if param_field and param_field != "":
            parameter = param[param_field]
            logger.debug(f"assert request body field: `{parameter}` and expected")
            validator = cls.parser(validator)
            expected = validator["val"]
            try:
                assert expected == parameter, f"actual result: {expected};but expected result: {parameter}"
            except AssertionError:
                flag = False
        else:
            logger.info("no requirement for assert request body and expected,ignored.")
        return flag

    @classmethod
    def db_assert(cls, validator: dict, dbinfo=None):
        """
        对比预期值和数据库存储值
            @validator:
            {
                "val": "zhang.wenke",
                "mode": 0,
                "type": 0,
                "field": "user_id",
                "expression": "$.user_id",
                "param_field": "username"
            }
        """
        flag = True
        if dbinfo:
            field = validator.get("field")
            if field and field != "":
                logger.info("assert database and expected")
                url, sql = dbinfo["url"], dbinfo["sql"]
                mysql = parse_mysql_dbinfo(url)
                if mysql:
                    db_rst = mysql.execute_query_as_dict(sql)
                    if len(db_rst) == 0:
                        logger.error(f"database is blank")
                        flag = False
                    else:
                        validator = cls.parser(validator)
                        expected = validator["val"]
                        db_rst = db_rst[0][field]
                        try:
                            assert expected == db_rst, f"actual result: {expected};but expected result: {db_rst}"
                        except AssertionError:
                            flag = False
                else:
                    flag=False
                    logger.error(f"fail to connect mysql,error: {traceback.format_exc()}")
            else:
                logger.info("no requirement for assert database and expected for this field,ignored")
        else:
            logger.info("no requirement for assert database and expected,ignored")
        return flag
