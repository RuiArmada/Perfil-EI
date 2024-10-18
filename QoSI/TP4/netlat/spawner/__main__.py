#!/usr/bin/python3

from spawner import DigitalOceanSpawner

if __name__ == '__main__':
    DigitalOceanSpawner('assets/digital_ocean/digital_ocean_launch_options.json', debug=True)