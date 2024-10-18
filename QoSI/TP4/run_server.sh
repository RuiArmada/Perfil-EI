#!/bin/bash
source ./.env/bin/activate
python3 netlat server --interface enp2s0 -s &
