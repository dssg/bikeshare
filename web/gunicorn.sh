#!/bin/bash
set -e
PROJECT=/home/ubuntu/bikeshare
LOGFILE=$PROJECT/run/gunicorn.log
LOGDIR=$(dirname $LOGFILE)
NUM_WORKERS=3
# user/group to run as
source /home/ubuntu/.bashrc
USER=ubuntu
cd $PROJECT/web
test -d $LOGDIR || mkdir -p $LOGDIR
exec gunicorn -w $NUM_WORKERS --bind 127.0.0.1:7777 --user=$USER  --log-level=debug --log-file=$LOGFILE 2>>$LOGFILE app:app -t 60