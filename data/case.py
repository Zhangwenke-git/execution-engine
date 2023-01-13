null = None
false = False
true = True

data_mapping_dict =  [{
    "exec_id": "EXEC_1952833615C84FC1B8958AFE432CA912",
    "body": [
        {
            "uid": "79a9204a6f1e4e4abc5b53d3f7c1aeee",
            "casetemplate": {
                "uid": "b1ac80c0b54b41038730f5aee4661269",
                "statue_display": "有效",
                "method_display": "POST",
                "dbinfo_config": "MYSQL|127.0.0.1|root||3306|djangovue",
                "statue": 1,
                "create_time": "2022-07-26 13:09:10",
                "update_time": "2022-07-26 13:09:10",
                "name": "auth_api",
                "url": "http://192.168.246.128:9000/api/auth",
                "method": 1,
                "header": {
                    "Connection": "keep-alive",
                    "Content-Type": "application/json"
                },
                "data": {
                    "password": "{{password}}",
                    "username": "{{username}}"
                },
                "expect": None,
                "process_name": "",
                "linux_order_str": "",
                "sql": "select * from userprofile;",
                "owner": "root",
                "dbinfo": 1,
                "redis": None,
                "mq": None,
                "ftp": None
            },
            "statue_display": "有效",
            "priority_display": "中",
            "module": "PORTAINER",
            "class_title": "容器云",
            "statue": 1,
            "create_time": "2022-07-26 14:06:38",
            "update_time": "2022-07-26 14:06:38",
            "case": "auth_api",
            "case_title": "认证接口",
            "case_description": "认证接口",
            "priority": 1,
            "owner": "root",
            "template": "b1ac80c0b54b41038730f5aee4661269",
            "testsuit": "b5cbd4de23ce4ec4af4b6a133e6694ba",
            "scenarios": [
                {
                    "uid": "e89f66400aba4138929cad7f073c6d56",
                    "statue_display": "有效",
                    "testcase": "auth_api",
                    "case_title": "认证接口",
                    "statue": 1,
                    "create_time": "2022-07-26 14:21:06",
                    "update_time": "2022-07-26 14:21:06",
                    "scenario": "用户名正确密码错误",
                    "parameter": [
                        {
                            "val": "aaaa1111@",
                            "type": 0,
                            "field": "password"
                        },
                        {
                            "val": "admin",
                            "type": 0,
                            "field": "username"
                        }
                    ],
                    "validator": [
                        {
                            "val": "zhang.wenke",
                            "mode": 0,
                            "type": 0,
                            "field": "user_id",
                            "expression": "$.user_id",
                            "param_field": "username"
                        }
                    ],
                    "owner": "root",
                    "cases": "79a9204a6f1e4e4abc5b53d3f7c1aeee"
                },
                {
                    "uid": "007c8bfcd5404c9bab19e1c790c76fac",
                    "statue_display": "有效",
                    "testcase": "auth_api",
                    "case_title": "认证接口",
                    "statue": 1,
                    "create_time": "2022-07-26 14:07:38",
                    "update_time": "2022-07-26 14:07:48",
                    "scenario": "用户名和密码均正确",
                    "parameter": [
                        {
                            "val": "aaaa1111!",
                            "type": 0,
                            "field": "password"
                        },
                        {
                            "val": "admin",
                            "type": 0,
                            "field": "username"
                        }
                    ],
                    "validator": [
                        {
                            "val": "root",
                            "mode": 0,
                            "type": 0,
                            "field": "user_id",
                            "expression": "$.user_id",
                            "param_field": "username"
                        }
                    ],
                    "owner": "root",
                    "cases": "79a9204a6f1e4e4abc5b53d3f7c1aeee"
                }
            ]
        }
    ]
}
]