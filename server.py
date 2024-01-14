#!/usr/bin/env python3

from richsockets.Server import richserver as rc
from richsockets.Server.richserver import print, inspect, console
rc.header()

import argparse

parser = argparse.ArgumentParser(
    formatter_class = argparse.RawDescriptionHelpFormatter,
    description = '''│ Myserver \033[4mclient side\033[0m script to interract with the socket server structure
│ in MyServerModule.py. Any available command to interract with the server
│ is provided in the CLI help utility to be invoked using h cmd ...''',
    epilog = 'Author : Pawlicki Loïc\n' + '─'*30 + '\n')

parser.add_argument('-d', '--delay', 
                    default = .3, 
                    type = float, 
                    metavar = '',
                    action= 'store',
                    help = '\tDelay to be passed to fake_process')

parser.add_argument('-r', '--res', 
                    default = 2000, 
                    type = int, 
                    metavar = '',
                    action= 'store',
                    help = 'Iterations to be passed to fake_process')

parser.add_argument('-p', '--path', 
                    default = 'DataBase', 
                    type = str, 
                    metavar = '',
                    action= 'store',
                    help = 'Path to be passed to tree tests')

parser.add_argument('-ip', '--ipserv', 
                    default = rc.get_dev_ip(), 
                    type = str, 
                    metavar = '',
                    action= 'store',
                    help = 'Server IPV4 adress to target')

parser.add_argument('-port', '--port',
                    default = 8000, 
                    type = int, 
                    metavar = '',
                    action= 'store',
                    help = 'Server port num to target')

args = parser.parse_args()
for arg in vars(args): print(arg, '\t─\t', getattr(args, arg))
# parser.print_help()


if __name__ == '__main__':

    rc.server_help()

    server = rc.Server(args.ipserv, args.port)
    server.serve(5)