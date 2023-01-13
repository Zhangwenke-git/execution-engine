import datetime
# from tools.regexp_utils import filter_tag
from tools.redis_utils import redis_
from tools.xml_parser import ParseXml
from tools.logger import logger
from config.settings import Settings

redis = redis_()

with open(Settings.template_file_path,"r",encoding="utf-8") as f:
    content = f.read()
    redis.set("template",content)


class AntReport:

    @classmethod
    def _generate_report_style_html(cls, data: dict, report_path):

        pyfile = data["exec_code"]
        start = data["start"]
        durations = float(data["durations"])
        total = int(data["total"])
        passed = int(data["passed"])
        errors = int(data["errors"])
        failed = int(data["failed"])
        skipped = int(data["skipped"])
        minimum = float(data["minimum"])
        maximum = float(data["maximum"])
        environment = data["environment"]
        passedRate = float('%.2f' % ((passed / total) * 100))
        average = float('%.2f' % (durations / total))
        environment_string = ""
        if isinstance(environment, dict):

            for key, value in environment.items():
                environment_string += '''
                    <tr>
                        <td>%s</td>
                        <td>%s</td>
                    </tr>

                ''' % (key, value)

        template = redis.get("template")
        html = template % (environment_string, datetime.datetime.strptime(start,"%Y-%m-%dT%H:%M:%S.%f").strftime('%Y-%m-%d %H:%M:%S'), total, errors, failed, passed, skipped, passedRate, average, minimum, maximum)

        for scenario in data["data"]:
            scenarioNm, description, cases = scenario.get("scenario"), scenario.get("description"), scenario.get(
                "cases")
            index = data["data"].index(scenario) + 1
            duration_list, outcome_list = [float(case.get("duration")) for case in cases], [case.get("outcome") for case
                                                                                            in cases]

            total = len(duration_list)
            max_time, min_time, aver_time = max(duration_list), min(duration_list), float(
                '%.2f' % (sum(duration_list) / total))

            passed, failed, skipped, error = outcome_list.count("Passed"), outcome_list.count(
                "Failed"), outcome_list.count(
                "Skipped"), outcome_list.count(
                "Error")

            passedRt = float('%.2f' % ((passed / total) * 100))


            if passed == total:
                color, flag = 'passed', '√'
                #color, flag = 'passed', '〓〓'
            elif skipped == total:
                color, flag = 'skipped', '∅'
                #color, flag = 'skipped', '〓〓'
            elif failed != 0:
                color, flag = 'failed', '×'
                #color, flag = 'failed', '〓〓'
            elif error != 0:
                color, flag = 'error', '〓〓'
            else:
                color, flag = '', ''

            html += '''
                <tbody class="%s results-table-row">
                
                    <tr class="scenario">
                        <td class="col-name" align="center">%d</td>
                        <td class="col-name">%s</td>
                        <td class="col-name">%d</td>
                        <td class="col-name">%d</td>
                        <td class="col-name">%d</td>
                        <td class="col-name">%d</td>
                        <td class="col-name">%s%%</td>
                        <td class="col-time">%s ms</td>
                        <td class="col-duration">%s ms</td>
                        <td class="col-links">%s ms</td>
                        <td class="col-result"  align="center"><span class="col-result button small white">%s</span></td>
                    </tr>
            
                    <tr>
                        <td class="extra" colspan="11">
                            <div>
                                <table width="99%%" class="details" id="case">
                                    <tr>
                                        <th>Order</th>
                                        <th>Case</th>
                                        <th>Iteration</th>
                                        <th>Duration(ms)</th>
                                        <th>Result</th>
                                        <th>Flag</th>
                                    </tr>
            ''' % (color, index, scenarioNm, error, failed, passed, skipped, passedRt, aver_time, min_time, max_time, flag)

            case_string = ""
            for case in cases:
                name, duration, outcome, times, errors, detail, parameter,log = case.get("name"), case.get(
                    "duration"), case.get(
                    "outcome"), case.get(
                    "times"), case.get("errors"), case.get("detail"), case.get("parameter"),case.get("log")
                order = str(index) + "-" + str(cases.index(case) + 1)
                if outcome == "Passed":
                    color, display = 'passed', 'display:None'
                elif outcome == "Failed":
                    color, display = 'failed', ''
                elif outcome == "Error":
                    color, display = 'error', ''
                else:
                    color, display = 'skipped', ''

                case_string += '''

                    <tr class="case">
                        <td align="center">%s</td>
                        <td>%s</td>
                        <td align="center">%s</td>
                        <td align="right">%s</td>
                        <td align="center" id="outcome" class="%s">%s</td>
                        <td align="center"><a style="%s" href="javascript:change('page_details_%s')"><img alt="expand/collapse" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQAQMAAAAlPW0iAAAABGdBTUEAALGPC/xhBQAAAAFzUkdCAK7OHOkAAAAGUExURSZ0pv///xB+eSAAAAAWSURBVAjXY2CAAcYGBJL/AULIIjAAAJJrBjcL30J5AAAAAElFTkSuQmCC"
                                                                                      id="page_details_%s_image"></a></td>
                    </tr>

                    <tr class="page_details" style="%s" id="page_details_%s">
                        <td colspan="11">
                            <div class="log" align="center">

                                <table class="loginfo">
                                    <tr align="left" style="color: red;">
                                        <td style="white-space: normal;background-color:#faebd7;"><h3><span class="button small orange">Error</span> </h3>'%s'</td>
                                    </tr>

                                    <tr>
                                        <td style="white-space: pre-wrap;background-color:#f5f5f5;"><h3 style="color:orange"><span class="button small orange">Details</span> </h3>%s</td>
                                    </tr>
                                    
                                    <tr>
                                        <td style="white-space: pre-wrap;background-color:#f5f5f5;"><h3 style="color:blue"><span class="button small orange">Logs</span> </h3>'%s'</td>
                                    </tr>

                                </table>
                            </div>
                        </td>
                    </tr>
                
   
                ''' % (
                    order, name, times, duration, color, outcome, display, order, order, display, order, errors, str(detail),str(log))
                    #order, name, times, duration, color, outcome, display, order, order, display, order, errors, filter_tag(str(detail)),filter_tag(str(log)))
            case_string += '''</table>
                        </div>
                    </td>
                </tr>
            </tbody>'''

            html += case_string
        html += '''</table>
            </body>
        </html>'''

        report_path = '%s/%s.html' % (report_path,pyfile)
        with open(report_path, 'w', encoding="utf-8") as f:
            f.write(html)
        return html


    @classmethod
    def create_ant_report(cls, report_path):
        xml_obj = ParseXml()
        try:
            data,summary= xml_obj.read_pytest_junit_xml(report_path)
        except IndexError:
            logger.info(f"Fail to parse report.xml under the path:{report_path} ")
        else:
            cls._generate_report_style_html(data, report_path)
            return data["durations"]

