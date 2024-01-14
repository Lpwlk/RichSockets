#!/usr/bin/env python3

from richsockets.Client import richclient as rc
from richsockets.Client.richclient import print, inspect, console

rc.header()

from rich.console import Group
from rich.panel import Panel
from rich.align import Align
from rich.prompt import Prompt, Confirm

import argparse

parser = argparse.ArgumentParser(
    formatter_class = argparse.RawDescriptionHelpFormatter,
    description = '''│ Myserver \033[4mclient side\033[0m script to interract with the socket server structure
│ in MyServerModule.py. Any available command to interract with the server
│ is provided in the CLI help utility to be invoked using h cmd ...''',
    epilog = 'Author : Pawlicki Loïc\n' + '─'*30 + '\n')
parser.add_argument('-d', '--delay', 
                    default = 2, 
                    type = float, 
                    metavar = '',
                    action= 'store',
                    help = '\tDelay to be passed to fake_process')
parser.add_argument('-r', '--res', 
                    default = 1000, 
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

grp = Group(
    Align(Panel("Hello", style="bold blue", expand = False, ), align='center'),
    Align(Panel("World", style="italic red"), align='center')
)

grp2 = Group(
    Panel("Hello", style="bold blue", expand = False,),
    Panel("World", style="italic red")
)

# print(Align(Panel(grp), align='center'))
# print(Panel(grp2))

if __name__ == '__main__':
    
    client = rc.Client(args.ipserv, args.port)
    client.connect()
    # client = myserv.Client('192.168.1.15', 8000)
    # rc.inspect(client)
    
    while True:
        try:
            inp = Prompt.ask('[bold green]Client command', default = 'h', show_default=False)
            client.log.info(f'Client object received input command : {inp}')
            match inp:
                case 'h': 
                    rc.client_help()
                case 't': 
                    client.get_temp()
                case 'p': 
                    client.ping_server()
                case 'b': 
                    client.broadcast()
                case 'si': 
                    client.get_sock_info()
                case 'sd':
                    client.send_file()
                case 'st': 
                    client.stream_channel()
                case 'db': 
                    client.get_dbp()
                case 'cl': 
                    client.close()
                case 'co':
                    client = client.Client(args.ipserv, args.port); client.connect()
                case 'devcmd': 
                    client.sendworkspace()
                case 'isocket': inspect(rc.socket.socket, methods=True)
                case 'iclient': inspect(rc.rich, methods=True)
                case _ :
                    print('[bold red]Error: Command unknown, see client help (h cmd) for available commands ...') 
                    client.log.error('Unknown user input in client command loop') 
                    pass
                
            rc.process(args.delay, args.res)
            
        except KeyboardInterrupt:
            print('[bold red]\t\nKeyboard interrupt -> Client socket closed')
            client.close()
            break