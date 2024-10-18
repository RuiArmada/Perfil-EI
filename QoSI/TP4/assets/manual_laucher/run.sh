#!/bin/bash
# Run the application
cd /netlat
. /netlat/.venv/bin/activate

echo "Starting worker"
python3 netlat worker &

echo "Bot started"
python3 netlat bot -b -r main &
