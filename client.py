#!/usr/bin/env python3

from richsockets.Client import richclient as rc

rc.header()

args = rc.client_argparse(verbose = 0)

if __name__ == '__main__':
    
    client = rc.Client(args.ipserv, args.port)
    client.run()
    
    # client.connect()
    # while True:
    #     try:
    #         cmd = client.get_command()
    #         match cmd:
    #             case 'h': 
    #                 rc.client_help()
    #             case 'p': 
    #                 client.ping_server()
    #             case 't': 
    #                 client.get_temp()
    #             case 'b': 
    #                 client.broadcast()
    #             case 'd':
    #                 client.print_attrs()
    #             case 'in':
    #                 client.self_inspect()
    #             case 'sd':
    #                 client.send_file()
    #             case 'st': 
    #                 client.stream_channel()
    #             case 'cl': 
    #                 client.close()
    #             case 'co':
    #                 client = rc.Client(args.ipserv, args.port); client.connect()
    #             case 'devcmd': 
    #                 client.sendworkspace()
    #             case 'isocket': 
    #                 rc.inspect(rc.socket.socket, methods=True)
    #             case _ :
    #                 print('[bold red]Error: Command unknown, see client help (h cmd) for available commands ...') 
    #                 client.log.error('Unknown user input in client command loop') 
    #                 pass
                
    #         # rc.process(args.delay, args.res)
    #         rc.process(args.delay)
            
    #     except KeyboardInterrupt:
    #         rc.console.print('[bold red]Keyboard interrupt -> Client socket closing ...')
    #         client.close()
    #         break