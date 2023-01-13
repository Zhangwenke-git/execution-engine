FROM python:3.10
RUN mkdir -p /home/app/engine
RUN mkdir -p /home/app/engine/log
RUN touch /home/app/engine/log/celery.log
WORKDIR /home/app/engine
COPY pip.conf /root/.pip/pip.conf
COPY requirements.txt /home/app/engine
RUN pip install -r /home/app/engine/requirements.txt
RUN rm -rf /home/app/engine
COPY . /home/app/engine

RUN chmod a+x /home/app/engine/start.sh

ENV SERVER_ADDRESS="None"
ENV DATA_ID="None"

ENTRYPOINT ./start.sh $SERVER_ADDRESS $DATA_ID


