from tools.config_loader import conf

sample = {
    "exec_id": "HEART_BEAT",
    "body": [
        {
            "casetemplate": {
                "dbinfo_config": None,
                "statue": 1,
                "name": "HEART_BEAT_CHECKER",
                "url": f"http://localhost:{int(conf('server.port'))}/heartbeat/send",
                "unit_flag": True,
                "method": "POST",
                "header": {
                    "Content-Type": "application/json",
                    "Connection": "keep-alive"
                },
                "data": {
                    "password": "{{password}}",
                    "username": "{{username}}"
                },
                "expect": None,
                "context": None,
                "files": None,
                "sql": "",
                "dbinfo": None,
                "redis": None,
                "mq": None,
                "ftp": None
            },
            "module": "HEAT_BEAT",
            "class_title": "HEAT_BEAT",
            "case": "send_beats",
            "case_title": "HEART_BEAT API",
            "case_description": "HEART_BEAT API",
            "scenarios": [
                ["NORMAL",
                 [
                     {
                         "val": "admin",
                         "type": 0,
                         "field": "username"
                     },
                     {
                         "val": "aaaa1111!",
                         "type": 0,
                         "field": "password"
                     }
                 ],
                 [
                     {
                         "val": "eyJ",
                         "mode": 2,
                         "type": 0,
                         "field": "",
                         "expression": "$.jwt",
                         "param_field": None
                     }
                 ]
                 ]
            ]
        }
	]
}
