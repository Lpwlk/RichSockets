import sys, time
import random
import struct
import threading
import hashlib
import os
import numpy as np
import socket
import logging
import platform
import mactemperatures
from datetime import datetime
from rich import inspect, print
import rich.rule as rule
import rich.table as table
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.table import Table
from rich.prompt import Prompt
import argparse

console = Console()
server_colors = ['blue','green','yellow','magenta','white']

###################    Request codes     ###################

class RequestCodes:
    AUTH = b'00'
    LOGIN = b'01'
    REGISTER = b'02'
    DEVBYPASS = b'03'
    PING = b'10'
    TEMP = b'20'
    BROADCAST = b'30'
    ATTRS = b'40'
    STREAM = b'50'
    DOWNLOAD = b'60'
    UPLOAD = b'70'
    DISCONNECT = b'80'
    SHUTDOWN = b'90'

###################    Response codes    ###################
 
class ResponseCodes:
    NAUTH = b'00'
    AUTH = b'01'
    OK = b'02'
    NOK = b'03'
    AUTHFAILED = b'04'

def translateRequest(code: bytes) -> str:
    for attr, val in RequestCodes.__dict__.items():
        if code == val: return attr
        
def translateResponse(code: bytes) -> str:
    for attr, val in ResponseCodes.__dict__.items(): 
        if code == val: return attr


################### General usage functions ###################

def header(color: str = 'yellow', lcolor: str = 'white') -> None:
    console.print(rule.Rule(style = lcolor))
    header = table.Table(title='Python script execution init ...', title_justify='center', border_style=lcolor, min_width=60, expand=True)
    header.add_column('Variable', style=color, header_style='bold '+color)
    header.add_column('Variable states', style='italic '+color, header_style='bold '+color)
    header.add_row('node.name',  f'{platform.uname().node} (OS: {platform.uname().system})')
    header.add_row('sys.argv',   f'{repr(sys.argv)}')
    header.add_row('sys.path',   f'{sys.path[0]}')
    console.print(header, justify = 'center')
    console.print(rule.Rule(style = lcolor))

def say(msg: str, voice: str = 'Samantha', rate: int = 160, vol: float = 0.5) -> None:
    os.system(f'say [\\[volm {vol}]] {msg} -v {voice} -r {rate}')

def notif(fname: str = 'Blow') -> None:
    os.system(f'afplay {os.path.dirname(__file__)}/SoundLib/{fname}')

notifs = sorted(os.listdir(f'{os.path.dirname(__file__)}/SoundLib/'))
print(notifs)
for snd in notifs:
    console.print(snd, style = 'bright_blue')
    notif(fname = snd)

def get_dev_ip(verbose: bool = False) -> str:
    ip = socket.gethostbyname(socket.gethostname())
    if verbose : 
        console.print(f'{socket.gethostbyname(socket.gethostname())=}')
        console.print(f'{socket.gethostname()=}')
    return ip

def get_time(hour: bool = True, date: bool = False) -> str:
    format = ''
    if hour: format += '%H:%M:%S'
    if date: format += '%d/%m/%Y'
    return datetime.now().strftime(format)

def sha256(data) -> str:
        return hashlib.sha256(data).hexdigest()
    
def process(delay: float = 1, res: int = 10) -> None:
    progress = Progress("{task.description}", SpinnerColumn(), BarColumn(), TextColumn("[progress.percentage]{task.percentage:>3.0f}%"), console = console)
    progress.add_task("Fake process", total=delay)
    with Live(progress):
        while not progress.finished:
            time.sleep(delay/res)
            progress.advance(0, delay/res)

def get_cpu_temp() -> float:
    opsystem = platform.system()
    if opsystem == "Linux": 
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as file: 
            return float(file.read().strip()) / 1000.0
    elif opsystem == "Darwin": 
        return float(mactemperatures.get_thermal_readings()['PMU tdie1'])

def get_socket_attrs(tcp_socket = socket, detailed: bool = True) -> Table:
    socket_table = Table(
        title=" > [underline]Socket attributes",
        title_justify = "left",
        border_style="white",
        min_width = None)
    socket_table.add_column('Attributes')
    socket_table.add_column('Values')
    socket_table.add_row('Remote Address', str(tcp_socket.getpeername()) if tcp_socket.getpeername() else 'Not connected')
    socket_table.add_row('Local Address', str(tcp_socket.getsockname()))
    if detailed: 
        socket_table.add_row('Socket Family', str(socket.AddressFamily(tcp_socket.family).name))
        socket_table.add_row('Socket TypeName', str(socket.SocketKind(tcp_socket.type).name))
        socket_table.add_row('Blocking Mode', '(Blocking)' if tcp_socket.gettimeout() else '(Non-blocking)')
        socket_table.add_row('Socket Protocol',str(tcp_socket.proto))
    else: 
        socket_table.add_row('Socket FTypeName', f'{socket.AddressFamily(tcp_socket.family).name} ⎥ {socket.SocketKind(socket.type).name} ' + ('(Blocking)' if socket.gettimeout() else '(Non-blocking)'))
    console.print(socket_table)
    return socket_table

def get_threading_table() -> None:
    threads_table = Table(
        title_justify = "center",
        border_style="white",
        min_width = None,
        )
    threads_table.add_column('Active threads', header_style = 'yellow italic')
    for thread in threading.enumerate(): 
        threads_table.add_row(thread.name)
    console.print(threads_table)

############### Client side rich-based routines ###############

def client_help() -> None:
    console.print(rule.Rule(style = 'white'), width = 80)
    help = table.Table(
        title=" > [underline]Client help utility : every available client commands are indexed here",
        title_justify = "left",
        border_style="white",
        min_width = 80,
        )
    help.add_column("Command", style="yellow", header_style="bold yellow")
    help.add_column("Associated client methods description", style="yellow", header_style="bold yellow")
    help.add_column("Dev state", style="italic")
    help.add_row("'h'",    "Display client-side help",             "dev_state")
    help.add_row("'p'",    "Ping server thread",                   "dev_state")
    help.add_row("'t'",    "Get server CPU temp",                  "dev_state")
    help.add_row("'b'",    "Broadcast data to available clients",  "dev_state")
    help.add_row("'st'",   "Send file to server database",         "dev_state")
    help.add_row("'cl'",   "Close current client socket",          "dev_state")
    help.add_row("'co'",   "Open new client socket",               "dev_state")
    console.print(help)

def init_client_log(log_num, show_path: bool = True, stream: bool = False) -> tuple[logging.Logger, str]:
    log_path = f'richsockets/Client/DataBase/Logs/log_client_{log_num}.log'
    if show_path: console.print(f'Client logs saved at : {log_path}')
    client_log = logging.getLogger('client_log')
    client_fileHandler = logging.FileHandler(filename = log_path, mode = 'w'); streamHandler = logging.StreamHandler()
    client_log.setLevel(logging.DEBUG); client_fileHandler.setLevel(logging.DEBUG); streamHandler.setLevel(logging.DEBUG)
    fmt = logging.Formatter(fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt = '%I:%M:%S')
    client_fileHandler.setFormatter(fmt); streamHandler.setFormatter(fmt)
    client_log.addHandler(client_fileHandler)
    if stream: client_log.addHandler(streamHandler)
    return client_log, log_path

def client_argparse(verbose: bool = True, help: bool = False) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        formatter_class = argparse.RawDescriptionHelpFormatter,
        description = '''│ Myserver \033[4mclient side\033[0m script to interract with the socket server structure
    │ in MyServerModule.py. Any available command to interract with the server
    │ is provided in the CLI help utility to be invoked using h cmd ...''',
        epilog = 'Author : Pawlicki Loïc\n' + '─'*30 + '\n')
    parser.add_argument('-d', '--delay', 
                        default = 1, type = float, 
                        metavar = '', action= 'store',
                        help = '\tDelay to be passed to fake_process')
    parser.add_argument('-r', '--res', 
                        default = 300, type = int, 
                        metavar = '', action= 'store',
                        help = 'Iterations to be passed to fake_process')
    parser.add_argument('-p', '--path', 
                        default = 'DataBase', type = str,
                        metavar = '', action= 'store',
                        help = 'Path to be passed to tree tests')
    parser.add_argument('-ip', '--ipserv', 
                        default = get_dev_ip(), type = str, 
                        metavar = '', action= 'store',
                        help = 'Server IPV4 adress to target')
    parser.add_argument('-port', '--port',
                        default = 8000, type = int, 
                        metavar = '', action= 'store',
                        help = 'Server port num to target')
    args = parser.parse_args()
    
    if verbose:
        for arg in vars(args): console.print(arg, '\t─\t', getattr(args, arg))
    if help:
        parser.print_help()   
    return args


############### Server side rich-based routines ###############
    
def init_server_log(show_path: bool = True, stream: bool = False) -> logging.Logger:
    log_path = 'richsockets/Server/DataBase/Logs/log_server.log'
    if show_path: console.print(f'Server logs saved at : {log_path}')
    server_log = logging.getLogger('server_log')
    server_fileHandler = logging.FileHandler(filename = log_path, mode = 'w'); streamHandler = logging.StreamHandler()
    server_log.setLevel(logging.DEBUG); server_fileHandler.setLevel(logging.DEBUG); streamHandler.setLevel(logging.DEBUG)
    fmt = logging.Formatter(fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(threadName)s)', datefmt = '%I:%M:%S')
    server_fileHandler.setFormatter(fmt); streamHandler.setFormatter(fmt)
    server_log.addHandler(server_fileHandler)
    if stream: server_log.addHandler(streamHandler)
    return server_log

def server_argparse(verbose: bool = True, help: bool = False) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        formatter_class = argparse.RawDescriptionHelpFormatter,
        description = '''│ Myserver \033[4mclient side\033[0m script to interract with the socket server structure
    │ in MyServerModule.py. Any available command to interract with the server
    │ is provided in the CLI help utility to be invoked using h cmd ...''',
        epilog = 'Author : Pawlicki Loïc\n' + '─'*30 + '\n')
    parser.add_argument('-d', '--delay', 
                        default = 1, type = float, 
                        metavar = '', action= 'store',
                        help = '\tDelay to be passed to fake_process')
    parser.add_argument('-r', '--res', 
                        default = 300, type = int, 
                        metavar = '', action= 'store',
                        help = 'Iterations to be passed to fake_process')
    parser.add_argument('-p', '--path', 
                        default = 'DataBase', type = str, 
                        metavar = '', action= 'store',
                        help = 'Path to be passed to tree tests')
    parser.add_argument('-ip', '--ipserv', 
                        default = get_dev_ip(), type = str, 
                        metavar = '', action= 'store',
                        help = 'Server IPV4 adress to target')
    parser.add_argument('-port', '--port',
                        default = 8000, type = int, 
                        metavar = '', action= 'store',
                        help = 'Server port num to target')
    parser.add_argument('-auth', '--auth',
                    default = True, type = bool, 
                    metavar = '', action= 'store',
                    help = 'Authentification flag')
    args = parser.parse_args()
    if verbose: 
        for arg in vars(args): console.print(arg, '\t─\t', getattr(args, arg))
    if help: 
        parser.print_help()    
    return args