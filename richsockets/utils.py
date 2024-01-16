import os
import sys
import time
import socket
import logging
import platform
import mactemperatures
from datetime import datetime
import numpy as np
from rich import print, inspect
import rich.rule as rule
import rich.table as table
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.table import Table

console = Console(highlighter = None)

###############################################################
################### General usage functions ###################
###############################################################

def header():
    console.print(rule.Rule(style = 'white'))
    header = table.Table(
        title="> Python script execution init ...",
        title_justify = "left",
        border_style="white",
        min_width = 60,
        expand=True
        )
    header.add_column("Variable", style="yellow", header_style="bold yellow")
    header.add_column("Variable states", style="italic yellow", header_style="bold yellow")
    header.add_row("node.name",  f'{platform.uname().node} (OS {platform.uname().system}')
    header.add_row("sys.argv",   f'{repr(sys.argv)}')
    header.add_row("sys.path",   f'{sys.path[0]}')
    console.print(header)

def get_dev_ip(verbose: bool = False):
    ip = socket.gethostbyname(socket.gethostname())
    if verbose : 
        console.print(f'{socket.gethostbyname(socket.gethostname())=}')
        console.print(f'{socket.gethostname()=}')
    return ip

def process(delay: float = 1, res: int = 1000):

    job_progress = Progress(
        "{task.description}",
        SpinnerColumn(),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console = console
    )
    
    job1 = job_progress.add_task("[green]Cooking", total=None)
    job2 = job_progress.add_task("[magenta]Baking", total=res)
    job3 = job_progress.add_task("[cyan]Mixing", total=2*res)

    total = sum(task.total if task.total is not None else 0 for task in job_progress.tasks)
    overall_progress = Progress()
    overall_task = overall_progress.add_task("All Jobs", total=int(total))

    progress_table = Table.grid()
    progress_table.add_row(
        Panel.fit(
            overall_progress, title="Overall Progress", border_style="green", padding=(2, 2)
        ),
        Panel.fit(job_progress, title="[b]Jobs", border_style="red", padding=(1, 2)),
    )

    with Live(progress_table, refresh_per_second=10):
        while not overall_progress.finished:
            time.sleep(delay/res)
            for job in job_progress.tasks:
                if not job.finished:
                    job_progress.advance(job.id)
            completed =  sum(task.completed if task.total is not None else 0 for task in job_progress.tasks)
            overall_progress.update(overall_task, completed=completed)


def get_client_details(tcp_socket = socket.socket, detailed: bool = False, verbose: bool = True,):
    socket_info = {
        'Remote Address  '  : tcp_socket.getpeername() if tcp_socket.getpeername() else 'Not connected',
        'Local Address   '  : tcp_socket.getsockname(),
        'Socket Family   '  : socket.AddressFamily(tcp_socket.family).name,
        'Socket TypeName '  : socket.SocketKind(tcp_socket.type).name,
        'Blocking Mode   '  : '(Blocking)' if tcp_socket.gettimeout() else '(Non-blocking)',
        'Socket Protocol '  : tcp_socket.proto,
        'Socket FTypeName'  : f'{socket.AddressFamily(tcp_socket.family).name} ⎥ {socket.SocketKind(tcp_socket.type).name}' + (' (Blocking)' if tcp_socket.gettimeout() else ' (Non-blocking)'),
        'Socket Hostname '  : socket.gethostname()
    }
    keys = list(socket_info)
    if verbose:
        for key in keys: 
            console.print(f'{key} {str(socket_info[key])}')
    return None


###############################################################
############### Client side rich-based routines ###############
###############################################################


def client_help():
    console.print(rule.Rule(style = 'white'), width = 80)
    help = table.Table(
        title=" > [underline]Client help utility[\] : every available client commands are indexed here",
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
    help.add_row("'sd'",   "Get socket details from server",       "dev_state")
    help.add_row("'sf'",   "Get socket details from server",       "dev_state")
    help.add_row("'st'",   "Send file to server database",         "dev_state")
    help.add_row("'cl'",   "Close current client socket",          "dev_state")
    help.add_row("'co'",   "Open new client socket",               "dev_state")
    help.add_row("'b'",    "Broadcast data to available clients",  "dev_state")
    console.print(help)

def init_client_log(log_num, verbose = 0, stream=0):
    log_path = f'richsockets/Client/DataBase/Logs/log_client_{log_num}.log'
    if verbose: console.print(f'Client logs saved at : {log_path}')
    client_log = logging.getLogger('client_log')
    client_fileHandler = logging.FileHandler(filename = log_path, mode = 'w'); streamHandler = logging.StreamHandler()
    client_log.setLevel(logging.DEBUG); client_fileHandler.setLevel(logging.DEBUG); streamHandler.setLevel(logging.DEBUG)
    fmt = logging.Formatter(fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt = '%I:%M:%S')
    client_fileHandler.setFormatter(fmt); streamHandler.setFormatter(fmt)
    client_log.addHandler(client_fileHandler)
    if stream: client_log.addHandler(streamHandler)
    return client_log, log_path


###############################################################
############### Server side rich-based routines ###############
###############################################################


def server_help():
    console.print(rule.Rule(style = 'white'), width = 80)
    help = table.Table(
        title=" > Server help utility: every available server commands are indexed here",
        title_justify = "left",
        border_style="white",
        min_width = 80,
        )
    help.add_column("Command", style="yellow", header_style="bold yellow")
    help.add_column("Associated server methods description", style="yellow", header_style="bold yellow")
    help.add_column("Dev state", style="italic")
    help.add_row("'h'",    "Display server-side help",             "dev_state")
    help.add_row("'p'",    "Ping server thread",                   "dev_state")
    console.print(help)
    
def init_server_log(verbose = 0, stream = 0):
    log_path = 'richsockets/Server/DataBase/Logs/log_server.log'
    if verbose: console.print(f'Server logs saved at : {log_path}')

    server_log = logging.getLogger('server_log')
    server_fileHandler = logging.FileHandler(filename = log_path, mode = 'w'); streamHandler = logging.StreamHandler()
    server_log.setLevel(logging.DEBUG); server_fileHandler.setLevel(logging.DEBUG); streamHandler.setLevel(logging.DEBUG)
    
    fmt = logging.Formatter(fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(threadName)s)', datefmt = '%I:%M:%S')
    server_fileHandler.setFormatter(fmt); streamHandler.setFormatter(fmt)

    server_log.addHandler(server_fileHandler)
    if stream: server_log.addHandler(streamHandler)
    return server_log

def get_cpu_temp():
    opsystem = platform.system()
    if opsystem == "Linux": 
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as file: 
            return float(file.read().strip()) / 1000.0
    elif opsystem == "Darwin": 
        return float(mactemperatures.get_thermal_readings()['PMU tdie1'])