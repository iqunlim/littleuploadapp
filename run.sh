#!/usr/bin/env bash
set -e 

if [ -z "${PORT}" ]; then
    PORT=5000
fi

# https://stackoverflow.com/questions/59895/how-do-i-get-the-directory-where-a-bash-script-is-located-from-within-the-script
SCRIPT_DIR=$(dirname "$0")

mkdir -p $SCRIPT_DIR/logs

echo "Gunicorn running on port $PORT"

gunicorn -w 4 \
-b 0.0.0.0:$PORT \
--access-logfile $SCRIPT_DIR/logs/flask.log \
--error-logfile $SCRIPT_DIR/logs/flask-err.log \
--capture-output \
'main:create_app()'