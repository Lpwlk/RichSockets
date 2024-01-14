#!/usr/bin/env python3

from richsockets.Client import richclient as client

from rich import print, inspect
from rich.console import Group
from rich.panel import Panel
from rich.align import Align
import rich

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
                    default = client.get_dev_ip(), 
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
# parser.print_help()
for arg in vars(args): print(arg, '\t─\t', getattr(args, arg))

grp = Group(
    Align(Panel("Hello", style="bold blue", expand = False, ), align='center'),
    Align(Panel("World", style="italic red"), align='center')
)

print(Align(Panel(grp), align='center'))

rich.inspect(client.Client(args.ipserv, args.port))

if __name__ == '__main__':
    client.header()

    # client = myserv.Client('192.168.1.15', 8000)
    client = client.Client(args.ipserv, args.port)
    client.connect()
    
    rich.inspect(client)
 
        
    while True:
        try:
            inp = input(' >>> ')
            client.log.info(f'Received input : {inp}')

            match inp:
                case 'h': client.client_help()
                case 't': client.get_temp()
                case 'p': client.ping_server()
                case 'b': client.broadcast()
                case 'si': client.get_sock_info()
                case 'sd': client.send_file()
                case 'sf': client.send_folder()
                case 'st': client.stream_channel()
                case 'db': client.get_dbp()
                case 'cl': client.close()
                case 'op': client = client.Client(args.ipserv, args.port); client.connect()
                case 'devcmd': client.sendworkspace()
                case _ :
                    print('[bold red]Error: Command unknown, see client help (h cmd) for available commands ...') 
                    client.log.error('Unknown user input in client command loop') 
                    pass

        except Exception as e:
            print(f'\t\nException occurend in ext. client loop : {e}', 'red')
            client.log.warning(f'Exception occurend in ext. client loop : {e}')

        except KeyboardInterrupt:
            print('[bold red]\t\nKeyboard interrupt -> Client socket closed')
            client.close()
            break