#!/bin/bash
# Send a message to the server
# Usage: send.sh server

server=$1

scp ./config.yaml root@$server:/netlat
scp ./run.sh root@$server:/

ssh root@$server "sh /run.sh"
