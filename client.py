#!/usr/bin/env python3

from richsockets.Client import richclient as myclient
import argparse
import rich
from mytools import cprint


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
                    default = 'ServerDataBase', 
                    type = str, 
                    metavar = '',
                    action= 'store',
                    help = 'Path to be passed to tree tests')
parser.add_argument('-ip', '--ipserv', 
                    default = myclient.get_dev_ip(), 
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


rich.inspect(myclient.Client(args.ipserv, args.port))
for arg in vars(args): 
    print(arg, '\t─\t', getattr(args, arg))

def custom_help():
    parser.print_help()
    for arg in vars(args): print(arg, '\t─\t', getattr(args, arg))
    # myserv.tree_recursive(args.path)
    # db_tree = myserv.dtree.display_tree(dir_path=myserv.os.path.join(myserv.os.getcwd(), args.path), max_depth=float("inf"), show_hidden=True, header = True)

if __name__ == '__main__':
    myclient.header()

    # client = myserv.Client('192.168.1.15', 8000)
    client = myclient.Client(args.ipserv, args.port)
    client.connect()
    
    while True:
        try:
            inp = input(' >>> ')
            client.log.info(f'Received input : {inp}')

            match inp:
                case 'h': custom_help()
                case 't': client.get_temp()
                case 'p': client.ping_server()
                case 'b': client.broadcast()
                case 'si': client.get_sock_info()
                case 'sd': client.send_file()
                case 'sf': client.send_folder()
                case 'st': client.stream_channel()
                case 'db': client.get_dbp()
                case 'cl': client.close()
                case 'op': client = myclient.Client(args.ipserv, args.port); client.connect()
                case 'hc': myclient.client_help()
                case 'devcmd': client.sendworkspace()
                case _ :
                    cprint('Error: Command unknown, see client help (h cmd) for available commands ...', 'red') 
                    client.log.error('Unknown user input in client command loop') 
                    pass

            myclient.fake_process(args.delay, args.res) 
        # except Exception as e:
        #     cprint(f'\t\nException occurend in ext. client loop : {e}', 'red')
        #     client.log.warning(f'Exception occurend in ext. client loop : {e}')

        except KeyboardInterrupt:
            cprint('\t\nKeyboard interrupt -> Client socket closed', 'red')
            client.close()
            break