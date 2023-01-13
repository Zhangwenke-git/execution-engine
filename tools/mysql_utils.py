import traceback
from pymysql import connect
from pymysql.cursors import DictCursor
from tools.logger import logger
from tools.set_single_instance import Singleton

class MySQL(connect,metaclass=Singleton):
    def __call__(self, sql, *args, **kwargs): #将类作为函数进行调用
        return self.execute_query_as_dict(sql)

    def execute_query_as_dict(self, sql):
        cur = super().cursor(DictCursor)
        try:
            logger.debug(f"prepare to execute query with sql: {sql}")
            cur.execute(sql)
        except Exception:
            logger.error(f"fail to get database data with `{sql}`,error as following:{traceback.format_exc()}")
        else:
            rows = cur.fetchall()
            super().commit()
            return rows
        finally:
            cur.close()


def parse_mysql_dbinfo(dbinfo: str, _class=MySQL):
    type_, host, user, password, port, database = dbinfo.split("|")
    if type_.upper() == "MYSQL":
        mysql = _class(host=host, user=user, password=password, port=int(port), database=database)
        return mysql
    else:
        return

