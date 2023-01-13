import os
from xml.dom import minidom

class ParseXml(object):

    @classmethod
    def process_case_name(cls,name):
        try:
            x,y = name.split("_EXEC_")
            import re
            z = re.findall(r'\[.+?\]',y)
            return x + ' : ' + z[0][1:-1].split('-')[0]
        except Exception:
            ...

    @classmethod
    def read_pytest_junit_xml(cls,xml_path):
        domTree = minidom.parse(os.path.join(xml_path, "JunitXml.xml"))
        testsuites = domTree.documentElement
        testsuite = testsuites.getElementsByTagName("testsuite")[0]

        xml_dict = {}
        start = testsuite.getAttribute("timestamp")
        durations = testsuite.getAttribute("time")
        total = testsuite.getAttribute("tests")
        errors = testsuite.getAttribute("errors")
        failed = testsuite.getAttribute("failures")
        skipped = testsuite.getAttribute("skipped")

        passed = int(total) - int(failed) - int(skipped) - int(errors)

        xml_dict["start"] = start
        xml_dict["durations"] = durations
        xml_dict["total"] = total
        xml_dict["failed"] = failed
        xml_dict["skipped"] = skipped
        xml_dict["passed"] = passed
        xml_dict["errors"] = errors

        environment_properties = testsuite.getElementsByTagName("properties")[0]
        environments = environment_properties.getElementsByTagName("property")

        environment_dict = {environment_.getAttribute("name"): environment_.getAttribute("value") for environment_ in environments}
        xml_dict["environment"] = environment_dict

        case_list, summary_list = [], []
        testcases = testsuite.getElementsByTagName("testcase")
        for testcase in testcases:
            case_dict, summary_dict = dict(), dict()
            scenario = testcase.getAttribute("classname")
            scenario ="::".join(scenario.split(".")[-2:])
            case_dict["scenario"], summary_dict["scenario"] = scenario, scenario
            summary_dict["start"] = start
            name = testcase.getAttribute("name").encode('utf-8').decode('unicode_escape')
            name = cls.process_case_name(name)
            case_dict["name"], summary_dict["name"] = name, name  # 将用例名称转换成中文
            case_dict["duration"] = testcase.getAttribute("time")
            case_dict["times"] = 1

            failure_list = testcase.getElementsByTagName("failure")
            error_list = testcase.getElementsByTagName("error")
            skip_list = testcase.getElementsByTagName("skipped")

            if len(failure_list) != 0:
                errors = failure_list[0].getAttribute("message")
                detail = failure_list[0].childNodes[0].data
                outcome = "Failed"

            elif len(skip_list) != 0:
                outcome = "Skipped"
                errors = skip_list[0].getAttribute("message")
                detail = skip_list[0].childNodes[0].data

            elif len(error_list) != 0:
                outcome = "Error"
                errors = error_list[0].getAttribute("message")
                detail = error_list[0].childNodes[0].data
            else:
                errors = ""
                detail = ""
                outcome = "Passed"

            case_dict["errors"] = errors
            case_dict["outcome"] = outcome
            case_dict["detail"] = detail

            summary_dict["outcome"] = outcome

            properties = testcase.getElementsByTagName("properties")
            if len(properties) != 0:
                parameters = properties[0]
                parameters_ = parameters.getElementsByTagName("property")
                parameter_dict = {parameter.getAttribute("name"): parameter.getAttribute("value") for parameter in
                                  parameters_}
                case_dict["parameter"] = parameter_dict

            system_err = testcase.getElementsByTagName("system-err")
            if len(system_err) != 0:
                log = system_err[0].childNodes[0].data
                case_dict["log"] = log

            case_list.append(case_dict)
            summary_list.append(summary_dict)

        scenario_name_list = [case.get("scenario") for case in case_list]
        durations_list = [float(case.get("duration")) for case in case_list]

        scenario_name_list = sorted(set(scenario_name_list), key=scenario_name_list.index)
        scenario_list = []
        for scenario_name in scenario_name_list:
            scenario_cases = []
            scenario_dict = dict()
            for case in case_list:
                try:
                    if scenario_name == case["scenario"]:
                        del case["scenario"]
                        scenario_cases.append(case)
                    scenario_dict["cases"] = scenario_cases
                    scenario_dict["scenario"] = scenario_name
                except KeyError:
                    ...
            scenario_list.append(scenario_dict)

        xml_dict["data"] = scenario_list
        xml_dict["minimum"] = min(durations_list)
        xml_dict["maximum"] = max(durations_list)
        xml_dict["exec_code"] = environment_dict["执行编码"]

        return xml_dict, summary_list
