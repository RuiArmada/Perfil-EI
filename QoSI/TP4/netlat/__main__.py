from server import Server
from worker import Worker
from bot import _run_from_modules

import argparse


def main(args):
    mode = args.mode
    interface = args.interface
    do_path = args.digital_ocean
    bot_mode = args.bot_mode
    bot_role = args.bot_role
    spawn = args.spawn

    if mode == "bot":
        _run_from_modules(bot_mode, bot_role)

    elif mode == "server":
        server = Server(interface, do_path, spawn)
        server.run()

    elif mode == "worker":
        worker = Worker(interface=interface)
        worker.start()

if __name__ == '__main__':
    args = argparse.ArgumentParser(description="NetLat")
    args.add_argument("mode", type=str, help="Mode of operation", choices=["server", "worker", "bot"])
    args.add_argument("--interface", type=str, help="Interface to bind to", default="eth1")
    args.add_argument("-o", "--digital_ocean", type=str, help="Digital Ocean launch path", default="assets/digital_ocean/digital_ocean_launch_options.json")
    args.add_argument("-s", "--spawn", action='store_true', help="Spawn DigitalOcean workers", default=False)
    args.add_argument("-b", "--bot_mode",action='store_true' , help="Run bot in admin mode", default=False)
    args.add_argument("-r", "--bot_role", type=str, help="Bot role",choices=["server","main","workers"], default="main")

    args = args.parse_args()
    print(args)

    main(args)
    
