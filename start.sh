#!/usr/bin/env bash
set -e
echo "SERVER_ADDRESS = ${SERVER_ADDRESS}"
echo "DATA_ID = ${DATA_ID}"
#main processor
python3 main.py &

#start celery work
celery -A celery_app worker -l info -f /home/app/engine/log/celery.log &

#start celery beat
celery -A celery_app beat --loglevel=info
