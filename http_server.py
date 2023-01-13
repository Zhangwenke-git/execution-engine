import traceback
from typing import Optional, List

import fastapi
import uvicorn
from pydantic import BaseModel

from tools.config_loader import conf
from tools.logger import logger
from tools.rabbitmq import amqp

app = fastapi.FastAPI()


class HeatBeat(BaseModel):
    username: str
    password: str


@app.post(path="/heartbeat/send")
async def heartbeat(heartbeat: HeatBeat):
    response = {
        "msg": "send heartbeat successfully",
        "result": True,
        "data": heartbeat.dict(),
        "code": 10200,
        "jwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwidXNlcm5hbWUiOiJhZG1pbiIsInJvbGUiOjEsInNjb3BlIjoiZGVmYXVsdCIsImZvcmNlQ2hhbmdlUGFzc3dvcmQiOmZhbHNlLCJleHAiOjE2NjQzNTYxNDcsImlhdCI6MTY2NDMyNzM0N30.ZS2nxb73GzCk1zklKYKw8gDm7gBUMJJ3QZ4cIQ2TTmQ"

    }
    return response


class Casetemplate(BaseModel):
    dbinfo_config: Optional[str] = None
    name: str
    url: str
    method: str
    header: dict
    data: Optional[dict] = {}
    sql: Optional[str] = None
    dbinfo: Optional[str] = None
    redis: Optional[str] = None
    ftp: Optional[str] = None
    mq: Optional[str] = None


class Case(BaseModel):
    casetemplate: Casetemplate
    module: str
    class_title: str
    case: str
    case_title: str
    case_description: str
    scenarios: list


class Execution(BaseModel):
    exec_id: str
    body: List[Case]


@app.post(path="/execute")
async def execute(message: Execution):
    exec_request_mq = amqp(conf("mq.request.queue"))

    try:
        exec_request_mq.basic_publish(message.dict(), conf("mq.pytest.exec.report.routing.key"))
    except Exception as e:
        logger.error(f"fail to publish message to execution engine,errors as following:{traceback.format_exc()}.")
        response = {
            "message": f"send message to rabbitmq failed,due to error {str(e)}",
            "result": True,
            "code": 10000
        }
    else:
        response = {
            "message": "send message to rabbitmq successfully",
            "result": True,
            "code": 10000
        }
    finally:
        exec_request_mq.close()

    return response


def httpserver():
    uvicorn.run("http_server:app", host="0.0.0.0", port=int(conf("server.port")), log_level="info", reload=False)
