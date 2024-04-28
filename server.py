#!/usr/bin/env python3

from richsockets.Server import richserver as rc

rc.header()

args = rc.server_argparse(verbose = 0)

if __name__ == '__main__':

    server = rc.Server(args.ipserv, args.port, args.auth)
    server.serve(5)