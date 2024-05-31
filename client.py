#!/usr/bin/env python3

from richsockets.Client import richclient as rc

rc.header()

args = rc.client_argparse(verbose = 0)

if __name__ == '__main__':
    
    client = rc.Client(args.ipserv, args.port)
    client.run()
