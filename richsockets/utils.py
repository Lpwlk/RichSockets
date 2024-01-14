import os
import sys
import time
import socket
import logging
import platform
import mactemperatures
from datetime import datetime
import numpy as np
from mytools import bprint, cprint

# import shutil
# shutil.make_archive('test', 'zip', 'ServerDataBase')

def header():
    cprint(' '+'-'*60, 'yellow')
    cprint(f' ⎹ > Python script execution init ...', 'yellow')
    cprint(f' ⎹ Node_name : {platform.uname().node} (OS {platform.uname().system})', 'yellow')
    cprint(f' ⎹ Sys.argv : {sys.argv}', 'yellow')
    cprint(f' ⎹ Location : {os.getcwd()}', 'yellow', end = '\n\n')
    
def init_client_log(log_num, verbose = 0, stream=0):
    log_path = f'richsockets/Client/DataBase/Logs/log_client_{log_num}.log'
    if verbose: print(f'Client logs saved at : {log_path}')

    client_log = logging.getLogger('client_log')
    client_fileHandler = logging.FileHandler(filename = log_path, mode = 'w'); streamHandler = logging.StreamHandler()
    client_log.setLevel(logging.DEBUG); client_fileHandler.setLevel(logging.DEBUG); streamHandler.setLevel(logging.DEBUG)

    fmt = logging.Formatter(fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt = '%I:%M:%S')
    client_fileHandler.setFormatter(fmt); streamHandler.setFormatter(fmt)

    client_log.addHandler(client_fileHandler)
    if stream: client_log.addHandler(streamHandler)
    return client_log, log_path

def client_help():
    cprint('\t'+'-'*70, 'yellow')
    cprint('\t> Client CLI help utility display, any command described here can be\n\tused to interract with the client via simple CLI command prompts ...', 'yellow')
    cprint('\t'+'-'*50, 'yellow')
    cprint('\t⎹ p :\tPing server thread', 'light_yellow')
    cprint('\t⎹ t :\tGet server CPU temp', 'light_yellow')
    cprint('\t⎹ b :\tBroadcast data to available clients', 'light_yellow')
    cprint('\t⎹ sd :\tGet socket details from server', 'light_yellow')
    cprint('\t⎹ sf :\tSend file to server database', 'light_yellow')
    cprint('\t⎹ st :\tSend data streaming request', 'light_yellow')
    cprint('\t⎹ db :\tGet database path from server', 'light_yellow')
    cprint('\t⎹ cl :\tClose current client socket', 'light_yellow')
    cprint('\t⎹ op :\tOpen new client socket', 'light_yellow')
    cprint('\t⎹ ch :\tDisplay client help', 'light_yellow')
    cprint('\t'+'-'*50, 'yellow')
    
def init_server_log(verbose = 0, stream = 0):
    log_path = 'richsockets/Server/DataBase/Logs/log_server.log'
    if verbose: print(f'Server logs saved at : {log_path}')

    server_log = logging.getLogger('server_log')
    server_fileHandler = logging.FileHandler(filename = log_path, mode = 'w'); streamHandler = logging.StreamHandler()
    server_log.setLevel(logging.DEBUG); server_fileHandler.setLevel(logging.DEBUG); streamHandler.setLevel(logging.DEBUG)
    
    fmt = logging.Formatter(fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(threadName)s)', datefmt = '%I:%M:%S')
    server_fileHandler.setFormatter(fmt); streamHandler.setFormatter(fmt)

    server_log.addHandler(server_fileHandler)
    if stream: server_log.addHandler(streamHandler)
    return server_log

def server_help():
    cprint('\t'+'-'*50, 'yellow')
    cprint('\t> Server CLI help utility display, any command\n\tdescribed here can be used to interract with\n\tthe server via simple CLI command prompts ...', 'yellow')
    cprint('\t'+'-'*50, 'yellow')
    cprint('\t⎹ h : Display server help', 'yellow')
    cprint('\t⎹ s : Start server ', 'yellow')
    cprint('\t'+'-'*50, 'yellow')
    

def get_dev_ip(verbose = 0):
    ip = socket.gethostbyname(socket.gethostname())
    if verbose : 
        print(f'\t{socket.gethostbyname(socket.gethostname())=}')
        print(f'\t{socket.gethostname()=}')
    return ip

def get_cpu_temp():
    opsystem = platform.system()
    if opsystem == "Linux": 
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as file: 
            return float(file.read().strip()) / 1000.0
    elif opsystem == "Darwin": 
        return float(mactemperatures.get_thermal_readings()['PMU tdie1'])
    
def get_socket_details(tcp_socket, color, clientID = hex(0), verbose = 0, detailed = 0):
    socket_info = {
        'Remote Address'    : tcp_socket.getpeername() if tcp_socket.getpeername() else 'Not connected',
        'Local Address '     : tcp_socket.getsockname(),
        'Socket Family '     : socket.AddressFamily(tcp_socket.family).name,
        'Socket TypeName'   : socket.SocketKind(tcp_socket.type).name,
        'Blocking Mode '     : '(Blocking)' if tcp_socket.gettimeout() else '(Non-blocking)',
        'Socket Protocol'   : tcp_socket.proto,
        'Socket FTypeName'   : f'{socket.AddressFamily(tcp_socket.family).name} ⎥ {socket.SocketKind(tcp_socket.type).name}' + (' (Blocking)' if tcp_socket.gettimeout() else ' (Non-blocking)'),
        'Socket Hostname'   : socket.gethostname()
    }
    
    info_str = ''
    for key, value in socket_info.items():
        if detailed:
            if key == 'Socket FTypeName': pass
            else: info_str += f'\t⎹ {key}\t->\t{value}\n'
        else: 
            if key == 'Socket Family ' or key == 'Socket TypeName' or key == 'Blocking Mode ' or key == 'Socket Protocol': pass
            else: info_str += f'\t⎹ {key}\t->\t{value}\n'
    if verbose:
        now = datetime.now()
        bprint([f'{now.strftime("%m/%d/%y - %H:%M:%S")}', 'Client socket details', f'16-bit ID: {clientID}'], color = color, box_color = color, width = 21, size = (1, 3))
        cprint(info_str, color)
    return info_str
from rich.console import Group
from rich.panel import Panel
from rich.align import Align
from rich.layout import Layout
from rich import layout
from rich import print, inspect
import rich

#### Client side rich-based routines






#### Server side rich-based routines














# grp = Group(
#     Align(Panel("Hello", style="bold blue", expand = False, ), align='center'),
#     Align(Panel("World", style="italic red"), align='center')
# )

# print(Align(Panel(grp), align='center'))

# """
# Demonstrates a Rich "application" using the Layout and Live classes.

# """

# from datetime import datetime

# from rich import box
# from rich.align import Align
# from rich.console import Console, Group
# from rich.layout import Layout
# from rich.panel import Panel
# from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
# from rich.syntax import Syntax
# from rich.table import Table

# console = Console()

# def make_layout() -> Layout:
#     """Define the layout."""
#     layout = Layout(name="root")

#     layout.split(
#         Layout(name="header", size=3),
#         Layout(name="main", ratio=1),
#         Layout(name="footer", size=7),
#     )
#     layout["main"].split_row(
#         Layout(name="side", ratio=2),
#         Layout(name="body", ratio=3, minimum_size=50),
#     )
#     layout["side"].split(Layout(name="box1"), Layout(name="box2"))
#     return layout


# def make_sponsor_message() -> Panel:
#     """Some example content."""
#     sponsor_message = Table.grid(padding=1)
#     sponsor_message.add_column(style="green", justify="right")
#     sponsor_message.add_column(no_wrap=True)
#     sponsor_message.add_row(
#         "Twitter",
#         "[u blue link=https://twitter.com/textualize]https://twitter.com/textualize",
#     )
#     sponsor_message.add_row(
#         "CEO",
#         "[u blue link=https://twitter.com/willmcgugan]https://twitter.com/willmcgugan",
#     )
#     sponsor_message.add_row(
#         "Textualize", "[u blue link=https://www.textualize.io]https://www.textualize.io"
#     )

#     message = Table.grid(padding=1)
#     message.add_column()
#     message.add_column(no_wrap=True)
#     message.add_row(sponsor_message)

#     message_panel = Panel(
#         Align.center(
#             Group("\n", Align.center(sponsor_message)),
#             vertical="middle",
#         ),
#         box=box.ROUNDED,
#         padding=(1, 2),
#         title="[b red]Thanks for trying out Rich!",
#         border_style="bright_blue",
#     )
#     return message_panel


# class Header:
#     """Display header with clock."""

#     def __rich__(self) -> Panel:
#         grid = Table.grid(expand=True)
#         grid.add_column(justify="center", ratio=1)
#         grid.add_column(justify="right")
#         grid.add_row(
#             "[b]Rich[/b] Layout application",
#             datetime.now().ctime().replace(":", "[blink]:[/]"),
#         )
#         return Panel(grid, style="white on blue")


# def make_syntax() -> Syntax:
#     code = """\
# def ratio_resolve(total: int, edges: List[Edge]) -> List[int]:
#     sizes = [(edge.size or None) for edge in edges]

#     # While any edges haven't been calculated
#     while any(size is None for size in sizes):
#         # Get flexible edges and index to map these back on to sizes list
#         flexible_edges = [
#             (index, edge)
#             for index, (size, edge) in enumerate(zip(sizes, edges))
#             if size is None
#         ]
#         # Remaining space in total
#         remaining = total - sum(size or 0 for size in sizes)
#         if remaining <= 0:
#             # No room for flexible edges
#             sizes[:] = [(size or 0) for size in sizes]
#             break
#         # Calculate number of characters in a ratio portion
#         portion = remaining / sum((edge.ratio or 1) for _, edge in flexible_edges)

#         # If any edges will be less than their minimum, replace size with the minimum
#         for index, edge in flexible_edges:
#             if portion * edge.ratio <= edge.minimum_size:
#                 sizes[index] = edge.minimum_size
#                 break
#         else:
#             # Distribute flexible space and compensate for rounding error
#             # Since edge sizes can only be integers we need to add the remainder
#             # to the following line
#             _modf = modf
#             remainder = 0.0
#             for index, edge in flexible_edges:
#                 remainder, size = _modf(portion * edge.ratio + remainder)
#                 sizes[index] = int(size)
#             break
#     # Sizes now contains integers only
#     return cast(List[int], sizes)
#     """
#     syntax = Syntax(code, "python", line_numbers=True)
#     return syntax


# job_progress = Progress(
#     "{task.description}",
#     SpinnerColumn(),
#     BarColumn(),
#     TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
# )
# job_progress.add_task("[green]Cooking")
# job_progress.add_task("[magenta]Baking", total=200)
# job_progress.add_task("[cyan]Mixing", total=400)

# total = sum(task.total for task in job_progress.tasks)
# overall_progress = Progress()
# overall_task = overall_progress.add_task("All Jobs", total=int(total))

# progress_table = Table.grid(expand=True)
# progress_table.add_row(
#     Panel(
#         overall_progress,
#         title="Overall Progress",
#         border_style="green",
#         padding=(2, 2),
#     ),
#     Panel(job_progress, title="[b]Jobs", border_style="red", padding=(1, 2)),
# )


# layout = make_layout()
# layout["header"].update(Header())
# layout["body"].update(make_sponsor_message())
# layout["box2"].update(Panel(make_syntax(), border_style="green"))
# layout["box1"].update(Panel(layout.tree, border_style="red"))
# layout["footer"].update(progress_table)


# from time import sleep

# from rich.live import Live

# with Live(layout, refresh_per_second=10, screen=True):
#     while not overall_progress.finished:
#         sleep(0.1)
#         for job in job_progress.tasks:
#             if not job.finished:
#                 job_progress.advance(job.id)
                
#         completed = sum(task.completed for task in job_progress.tasks)
#         overall_progress.update(overall_task, completed=completed)