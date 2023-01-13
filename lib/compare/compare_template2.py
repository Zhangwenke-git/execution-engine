# coding:utf-8

from src.Utils.Public.DictUtil import DictUtils
from config.path_config import attachment_html


class GenerateCompareReport:
    def __init__(self, mapping_dict=None):
        """
        :function：定义字段和字段list之间的映射，如果没有传输mapping_dict默认传值为--
        :param mapping_dict:
        """
        self.mapping_dict = mapping_dict

    def __xchange(self, dict_param, key):
        """
        :function:取出key在一个映射关系中的子key，之后取出dict_param中的value值
        :param dict_param: 其中一个字典
        :param key: 多个字典公用的key
        :return:
        """
        if self.mapping_dict and isinstance(self.mapping_dict, dict):
            res = []
            if key in self.mapping_dict.keys():
                for i in self.mapping_dict[key]:
                    res.append(dict_param.get(i))
                try:
                    string = [str for str in res if str not in [None]][0]  # res=[None,value,None,None...] 此行主要是删除None，保留第一个value
                except IndexError:
                    string = '漏配主键:'+key
            else:
                string = dict_param[key]
        else:
            try:
                string = dict_param[key]
            except KeyError:
                string = f'未配置{key}的映射关系'
        return string

    def _generateCNHtml(self, *args, cn_map_dic=None, black_list=None,skipped_list=None):
        """
        :function: 处理字段，传入(dict1,dict2,dict3...)或者[dict1,dict2,dict3...],取第一个dict1作为预期值，也是对比的标准
        :param args: 索要对比的dict,(dict1,dict2,dict3...)或者[dict1,dict2,dict3...]
        :param cn_map_dic: 中英文字段映射dict
        :param black_list: 设置黑名单，黑名单内的公用key不再对比，skipped_list忽略的字段，不做对比操作
        :return:返回元组，供函数_generateHtml中的*args使用
        """
        tem_dict_list = []
        for i in range(len(*args)):  # 自动更具*args的长度来生成对应的空字典
            exec('dict' + str(i) + ' = ' + "{}")
            tem_dict_list.append(eval('dict' + str(i)))

        compareResult, field_cn = [], []
        fieldList, compareList,passinfo= DictUtils().multcompare(list(*args),black_list,skipped_list)

        for index, key in enumerate(fieldList):
            for iindex, Dict in enumerate(tem_dict_list):
                Dict[key] = self.__xchange(list(*args)[iindex], key)

            flag = "失败"
            if compareList[index]=="passed":
                flag = "通过"
            elif compareList[index]=="skipped":
                flag = "跳过"
            compareResult.append(flag)

        if not cn_map_dic:
            cn_map_dic = dict()
        for key in fieldList:
            temp = "未映射中文名称"
            if key in list(cn_map_dic.keys()):
                temp = cn_map_dic[key]
            field_cn.append(temp)

        return fieldList, field_cn, list(tem_dict_list[0].values()), list(tem_dict_list[1].values()), list(
        ), list(), compareResult,passinfo

    def _generateHtml(self, senerioName, *args,
                      url='未配置',message2='TBS-DP-0039'):
        """

        :param senerioName: HTML文件的名称，和HTML中的标题
        :param args: _generateCNHtml的返回值
        :param message1: 消息列的名称，如TBS-DP-0039
        :param message2:
        :param message3:
        :param message4:
        :return: HTML文件，可浏览器打开
        """
        passinfo = list(*args)[-1]
        html = '''
        <!DOCTYPE html>
            <html>
              <head>
                <meta charset="utf-8"/>
                <title>中国外汇交易中心</title>

                <link href="../tools/bootstrap-3.3.7-dist/css/bootstrap.min.css" rel="stylesheet">


                <style>body {
                font-family: Helvetica, Arial, sans-serif;
                font-size: 12px;
                /* do not increase min-width as some may use split screens */
                min-width: 800px;
                color: #999;
            }

            h1 {
                font-size: 24px;
                color: black;
            }

            h2 {
                font-size: 16px;
                color: black;
            }

            p {
                color: black;
            }

            a {
                color: #999;
            }

            table {
                border-collapse: collapse;
            }

            /******************************
             * SUMMARY INFORMATION
             ******************************/

            #environment td {
                padding: 5px;
                border: 1px solid #E6E6E6;
            }

            #environment tr:nth-child(odd) {
                background-color: #f6f6f6;
            }

            /******************************
             * TEST RESULT COLORS
             ******************************/
            span.passed, .passed .col-result {

                color: green;
                border-radius: 12px;
                padding: 3px 14px;
                cursor: pointer;
                border: 1px solid green;

            }
            span.skipped, span.xfailed, span.rerun, .skipped .col-result, .xfailed .col-result, .rerun .col-result {
                color: gray;
                border-radius: 12px;
                padding: 3px 14px;
                cursor: pointer;
                border: 1px solid gray;
            }
            span.error, span.failed, span.xpassed, .error .col-result, .failed .col-result, .xpassed .col-result  {
                color: red;
                border-radius: 12px;
                padding: 3px 14px;
                cursor: pointer;
                border: 1px solid red;
            }


            /******************************
             * RESULTS TABLE
             *
             * 1. Table Layout
             * 2. Extra
             * 3. Sorting items
             *
             ******************************/

            /*------------------
             * 1. Table Layout
             *------------------*/

            #results-table {
                border: 1px solid #e6e6e6;
                color: #999;
                font-size: 12px;
                width: 100%%ds
            }

            #results-table th, #results-table td {
                padding: 5px;
                border: 1px solid #E6E6E6;
                text-align: left
            }
            #results-table th {
                font-weight: bold
            }

            /*------------------
             * 2. Extra
             *------------------*/

            .log:only-child {
                height: inherit
            }
            .log {
                background-color: #e6e6e6;
                border: 1px solid #e6e6e6;
                color: black;
                display: block;
                font-family: "Courier New", Courier, monospace;
                height: 230px;
                overflow-y: scroll;
                padding: 5px;
                white-space: pre-wrap
            }
            div.image {
                border: 1px solid #e6e6e6;
                float: right;
                height: 240px;
                margin-left: 5px;
                overflow: hidden;
                width: 320px
            }
            div.image img {
                width: 320px
            }
            .collapsed {
                display: none;
            }
            .expander::after {
                content: " (show)";
                color: #BBB;
                font-style: italic;
                cursor: pointer;
            }
            .collapser::after {
                content: " (hide)";
                color: #BBB;
                font-style: italic;
                cursor: pointer;
            }

            /*------------------
             * 3. Sorting items
             *------------------*/
            .sortable {
                cursor: pointer;
            }

            .sort-icon {
                font-size: 0px;
                float: left;
                margin-right: 5px;
                margin-top: 5px;
                /*triangle*/
                width: 0;
                height: 0;
                border-left: 8px solid transparent;
                border-right: 8px solid transparent;
            }

            .inactive .sort-icon {
                /*finish triangle*/
                border-top: 8px solid #E6E6E6;
            }

            .asc.active .sort-icon {
                /*finish triangle*/
                border-bottom: 8px solid #999;
            }

            .desc.active .sort-icon {
                /*finish triangle*/
                border-top: 8px solid #999;
            }
            </style></head>
              <body onLoad="init()">
                <script>/* This Source Code Form is subject to the terms of the Mozilla General
             * License, v. 2.0. If a copy of the MPL was not distributed with this file,
             * You can obtain one at http://mozilla.org/MPL/2.0/. */


            function toArray(iter) {
                if (iter === null) {
                    return null;
                }
                return Array.prototype.slice.call(iter);
            }

            function find(selector, elem) {
                if (!elem) {
                    elem = document;
                }
                return elem.querySelector(selector);
            }

            function find_all(selector, elem) {
                if (!elem) {
                    elem = document;
                }
                return toArray(elem.querySelectorAll(selector));
            }

            function sort_column(elem) {
                toggle_sort_states(elem);
                var colIndex = toArray(elem.parentNode.childNodes).indexOf(elem);
                var key;
                if (elem.classList.contains('numeric')) {
                    key = key_num;
                } else if (elem.classList.contains('result')) {
                    key = key_result;
                } else {
                    key = key_alpha;
                }
                sort_table(elem, key(colIndex));
            }

            function show_all_extras() {
                find_all('.col-result').forEach(show_extras);
            }

            function hide_all_extras() {
                find_all('.col-result').forEach(hide_extras);
            }

            function show_extras(colresult_elem) {
                var extras = colresult_elem.parentNode.nextElementSibling;
                var expandcollapse = colresult_elem.firstElementChild;
                extras.classList.remove("collapsed");
                expandcollapse.classList.remove("expander");
                expandcollapse.classList.add("collapser");
            }

            function hide_extras(colresult_elem) {
                var extras = colresult_elem.parentNode.nextElementSibling;
                var expandcollapse = colresult_elem.firstElementChild;
                extras.classList.add("collapsed");
                expandcollapse.classList.remove("collapser");
                expandcollapse.classList.add("expander");
            }

            function show_filters() {
                var filter_items = document.getElementsByClassName('filter');
                for (var i = 0; i < filter_items.length; i++)
                    filter_items[i].hidden = false;
            }

            function add_collapse() {
                // Add links for show/hide all
                var resulttable = find('table#results-table');
                var showhideall = document.createElement("p");
                showhideall.innerHTML = '<a href="javascript:show_all_extras()">unfold</a> / ' +
                                        '<a href="javascript:hide_all_extras()">collapse</a>';
                resulttable.parentElement.insertBefore(showhideall, resulttable);

                // Add show/hide link to each result
                find_all('.col-result').forEach(function(elem) {
                    var collapsed = get_query_parameter('collapsed') || 'Passed';
                    var extras = elem.parentNode.nextElementSibling;
                    var expandcollapse = document.createElement("span");
                    if (collapsed.includes(elem.innerHTML)) {
                        extras.classList.add("collapsed");
                        expandcollapse.classList.add("expander");
                    } else {
                        expandcollapse.classList.add("collapser");
                    }
                    elem.appendChild(expandcollapse);

                    elem.addEventListener("click", function(event) {
                        if (event.currentTarget.parentNode.nextElementSibling.classList.contains("collapsed")) {
                            show_extras(event.currentTarget);
                        } else {
                            hide_extras(event.currentTarget);
                        }
                    });
                })
            }

            function get_query_parameter(name) {
                var match = RegExp('[?&]' + name + '=([^&]*)').exec(window.location.search);
                return match && decodeURIComponent(match[1].replace(/\+/g, ' '));
            }

            function init () {
                reset_sort_headers();

                add_collapse();

                show_filters();

                sort_column(find('.initial-sort'));

                find_all('.sortable').forEach(function(elem) {
                    elem.addEventListener("click",
                                          function(event) {
                                              sort_column(elem);
                                          }, false)
                });

            };

            function sort_table(clicked, key_func) {
                var rows = find_all('.results-table-row');
                var reversed = !clicked.classList.contains('asc');
                var sorted_rows = sort(rows, key_func, reversed);
                /* Whole table is removed here because browsers acts much slower
                 * when appending existing elements.
                 */
                var thead = document.getElementById("results-table-head");
                document.getElementById('results-table').remove();
                var parent = document.createElement("table");
                parent.id = "results-table";
                parent.appendChild(thead);
                sorted_rows.forEach(function(elem) {
                    parent.appendChild(elem);
                });
                document.getElementsByTagName("BODY")[0].appendChild(parent);
            }

            function sort(items, key_func, reversed) {
                var sort_array = items.map(function(item, i) {
                    return [key_func(item), i];
                });

                sort_array.sort(function(a, b) {
                    var key_a = a[0];
                    var key_b = b[0];

                    if (key_a == key_b) return 0;

                    if (reversed) {
                        return (key_a < key_b ? 1 : -1);
                    } else {
                        return (key_a > key_b ? 1 : -1);
                    }
                });

                return sort_array.map(function(item) {
                    var index = item[1];
                    return items[index];
                });
            }

            function key_alpha(col_index) {
                return function(elem) {
                    return elem.childNodes[1].childNodes[col_index].firstChild.data.toLowerCase();
                };
            }

            function key_num(col_index) {
                return function(elem) {
                    return parseFloat(elem.childNodes[1].childNodes[col_index].firstChild.data);
                };
            }

            function key_result(col_index) {
                return function(elem) {
                    var strings = ['Error', 'Failed', 'Rerun', 'XFailed', 'XPassed',
                                   'Skipped', 'Passed'];
                    return strings.indexOf(elem.childNodes[1].childNodes[col_index].firstChild.data);
                };
            }

            function reset_sort_headers() {
                find_all('.sort-icon').forEach(function(elem) {
                    elem.parentNode.removeChild(elem);
                });
                find_all('.sortable').forEach(function(elem) {
                    var icon = document.createElement("div");
                    icon.className = "sort-icon";
                    icon.textContent = "vvv";
                    elem.insertBefore(icon, elem.firstChild);
                    elem.classList.remove("desc", "active");
                    elem.classList.add("asc", "inactive");
                });
            }

            function toggle_sort_states(elem) {
                //if active, toggle between asc and desc
                if (elem.classList.contains('active')) {
                    elem.classList.toggle('asc');
                    elem.classList.toggle('desc');
                }

                //if inactive, reset all other functions and add ascending active
                if (elem.classList.contains('inactive')) {
                    reset_sort_headers();
                    elem.classList.remove('inactive');
                    elem.classList.add('active');
                }
            }

            function is_all_rows_hidden(value) {
              return value.hidden == false;
            }

            function filter_table(elem) {
                var outcome_att = "data-test-result";
                var outcome = elem.getAttribute(outcome_att);
                class_outcome = outcome + " results-table-row";
                var outcome_rows = document.getElementsByClassName(class_outcome);

                for(var i = 0; i < outcome_rows.length; i++){
                    outcome_rows[i].hidden = !elem.checked;
                }

                var rows = find_all('.results-table-row').filter(is_all_rows_hidden);
                var all_rows_hidden = rows.length == 0 ? true : false;
                var not_found_message = document.getElementById("not-found-message");
                not_found_message.hidden = !all_rows_hidden;
            }
            </script>

                <h1>%s</h1>

                <h2>Environment</h2>
                <table id="environment">

                  <tr>
                    <td>所属部门</td>
                    <td>新本币测试部</td>
                  </tr>

                  <tr>
                    <td>项目名称</td>
                    <td>新本币项目</td>
                  </tr>

                  <tr>
                    <td>服务器地址</td>
                    <td>58.246.35.21</td>
                  </tr>
                  <tr>
                    <td>接口地址</td>
                    <td><a href="%s" target="_blank">%s</a></td>
                  </tr>

                </table>


                <h2 class="filter" hidden="true">Filter</h2>
                <input checked="true" class="filter" data-test-result="passed" hidden="true" name="filter_checkbox" onChange="filter_table(this)" type="checkbox"/><span class="passed">通过</span>
                <input checked="true" class="filter" data-test-result="failed" hidden="true" name="filter_checkbox" onChange="filter_table(this)" type="checkbox"/><span class="failed">失败</span>
                <input checked="true" class="filter" data-test-result="skipped" hidden="true" name="filter_checkbox" onChange="filter_table(this)" type="checkbox"/><span class="skipped">跳过</span>
                <h2>Result</h2>
                <h3>
                    <b><span style="color: orange">%s </span> fields in totle,failed<span style="color: red"> %s</span>, pass rate: </b>
                    <span style="width:auto;display:inline;color:green">%s</span>
                </h3>
                <table id="results-table" class="table table-striped">
                  <thead id="results-table-head">
                    <tr style='background-color :Teal'>
                      <th class="sortable time initial-sort" col="time">字段英文名称</th>
                      <th class="sortable time" col="time">字段中文名称</th>

                      <th>预期结果</th>
                      <th>%s</th>
                      <th class="sortable time" col="time">对比结果</th>

                    <tr hidden="true" id="not-found-message">
                      <th colspan="8">No results found. Try to check the filters</th></tr></thead>


               ''' % (senerioName,url,url,passinfo[0],passinfo[1],passinfo[2], message2)
        filedList = list(*args)[0]
        field_cn = list(*args)[1]
        compareResult = list(*args)[-2]
        for i in range(len(filedList)):
            color = 'MediumVioletRed'
            flag = 'failed'
            if compareResult[i] == "通过":
                flag = 'passed'
                color = 'SeaGreen'
            elif compareResult[i] == "跳过":
                flag = 'skipped'
                color = 'gray'
            html += '''
                        <tbody class="%s results-table-row">
            <tr>
              <td class="col-time">%s</td>
              <td class="col-time">%s</td>
              <td class="col-name" style="color:orange;font-weight:bolder">%s</td>
              <td>%s</td>
              <td class="col-time" style='background-color: %s'>%s</td>
            <tr>
                        ''' % (
                flag, filedList[i], field_cn[i], list(*args)[2][i], list(*args)[3][i],
                color,
                compareResult[i])

        html += '''</tbody></table></body></html> '''

        with open('%s/%s.html' % (attachment_html, senerioName), 'w', encoding="utf-8") as f:
            f.write(html)
        f.close()
        return html


if __name__ == "__main__":
    dict1 ={'calc_agnt': '交易双方', 'clrng_mthd': '双边自行清算', 'prc': '32.8718', 'vol': '120', 'prd': '6Y', 'mrty_dt': '2026/09/18', 'vl_dt': '2020/09/18', 'frst_prd_efctv_dt': '2020/09/18', 'intrst_adj': '实际天数', 'pymnt_dt_adj': '经调整的下一营业日', 'sprds': '0.00', 'fltng_leg_pymnt_prd': '季', 'fltng_leg_frst_rglr_pymnt_dt': '2020/12/18', 'fltng_leg_rst_frqncy': '季', 'fltng_leg_frst_dtrmn_dt': '2020/09/18', 'fltng_leg_intrst_mthd': '单利', 'fltng_leg_intrst_bss': '实际/360', 'fxng_leg_pymnt_prd': '季', 'fxng_leg_frst_rglr_pymnt_dt': '2020/12/18', 'fxng_leg_intrst_bss': '实际/365', 'ref_intrst_rate_nm': 'Shibor_3M', 'splmntry_term': '—', '_ngtt_qt_src_errmsg': '对话', '_qt_dir': '支付固定利率', 'rivalTrdActCnShrtNm': '农业银行', 'selfTrdActCnShrtNm': '中信证券', 'tra_tl_cd': 'Shibor3M_6Y', 'clrngSt': '无', 'cpTrdrNm': '杨穆彬', 'exrcsCd': '—', 'realTmUndtkF': '否'}

    dict2 = {'qt_cd': '200917060201000005', 'selfInstant': '中信证券', 'selfTrdActCnShrtNm': '中信证券', 'selfTrdr': '张惠梓', 'dir': '支付固定利率', 'rivalInstant': '农业银行', 'rivalTrdActCnShrtNm': '农业银行', 'rivalTrdr': '杨穆彬', 'qt_st': '成交', 'tra_tl_cd': 'Shibor3M_6Y', 'ref_intrst_rate_nm': 'Shibor_3M', 'fixIntrstRate': '32.8718', 'vol': '120', 'prd': '6Y', 'vl_dt': '2020-09-18', 'mrty_dt': '2026-09-18', 'frst_prd_efctv_dt': '2020-09-18', 'intrst_adj': '实际天数', 'pymnt_dt_adj': '经调整的下一营业日', 'clrng_mthd': '双边自行清算', 'calc_agn': '交易双方', 'sprds': '0.00', 'fltng_leg_rst_frqncy': '季', 'fltng_leg_pymnt_prd': '季', 'fltng_leg_frst_dtrmn_dt': '2020-09-18', 'fltng_leg_intrst_mthd': '单利', 'fltng_leg_intrst_bss': '实际/360', 'fltng_leg_frst_rglr_pymnt_dt': '2020-12-18', 'fxng_leg_pymnt_prd': '季', 'fxng_leg_intrst_bss': '实际/365', 'splmntry_term': ''}
    from data.字段映射.CN_ENmapping import ndm_irs_en_cn_mapping
    from src.Utils.Compare.MappingConfig import mapping_dict
    sample = GenerateCompareReport(mapping_dict)

    dict_tuple = (dict1, dict2)

    field_result = sample._generateCNHtml(dict_tuple, cn_map_dic=ndm_irs_en_cn_mapping, black_list=None,skipped_list=["fltng_leg_frst_dtrmn_dt","mrty_dt"])

    html = sample._generateHtml("2条信息对比", field_result)
