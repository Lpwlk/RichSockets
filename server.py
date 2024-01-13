#!/usr/bin/env python3

from richsockets.Server import richserver as myserv
import rich

rich.inspect(myserv.Server(myserv.get_dev_ip(), 8000))
# rich.inspect(rich.inspect, all = True)
# rich.Confirm().ask('R u ok ?')
if __name__ == '__main__':

    myserv.header()

    server = myserv.Server(myserv.get_dev_ip(), 8000)
    server.serve(5)