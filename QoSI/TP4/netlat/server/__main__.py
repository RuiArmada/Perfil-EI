#!/usr/bin/python3

from server import Server

if __name__ == '__main__':
    server = Server("lo","../assets/digital_ocean/digital_ocean_launch_options.json")
    server.run()


