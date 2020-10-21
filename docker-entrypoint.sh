#!/bin/sh

python3 -m yaskawa-convert-status-into-event
/bin/sh -c "sleep 3"
curl -s -X POST localhost:10001/quitquitquit
