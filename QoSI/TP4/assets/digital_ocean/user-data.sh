#!/bin/bash
apt-get install -y git python3-venv python3-pip
# Clone the repository
git clone https://auth2:\<token_v2\>@github.com/MayorX500/disQoSi.git /netlat
# Setup Python virtual environment in the cloned directory
cd /netlat
echo -ne "channels:\n  category: id\n  logs: id\n  voice: id\ncredentials:\n  main: <token_main>\n  server: <token_server>\n  workers: <token_workers>\nguild:\n  id: id\n" >config.yaml
python3 -m venv .venv
source .venv/bin/activate
# Install dependencies from requirements file
pip install -r requirements.txt
# Run the Python script
python3 netlat worker &
python3 netlat bot -r main -b &
#python3 legion & disown
