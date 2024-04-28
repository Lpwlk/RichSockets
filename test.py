# import time
# from mytools import *
# import numpy as np
# import argparse
# import rich
# from rich.columns import Columns

# parser = argparse.ArgumentParser(
#    formatter_class=argparse.RawDescriptionHelpFormatter,
#    description="Python3 test utility for MyServer project developement",
#    epilog='Author : Pawlicki Loïc'
#    )
# parser.add_argument('-d', '--delay', 
#    default = 0.05, type = float, metavar = '',
#    action= 'store', help = '\tDelay to be passed to value print loop')

# parser.add_argument('-m', '--mod_bit', 
#    default = 3, type = int, metavar = '',
#    action= 'store', help = '\tDelay to be passed to fake_process')

# parser.add_argument('-i', '--iterations', 
#    default = 32, type = int, metavar = '',
#    action= 'store', help = '\tDelay to be passed to fake_process')

# # rich.inspect(rich)

# args = parser.parse_args()
# argstable = rich.table.Table()

# console = rich.console.Console()
# rich.align.Align.center(argstable)

# argstable.add_column('Args'.center(16))
# for arg in vars(args): 
#    argstable.add_row(arg, f'{getattr(args, arg)}')

# panel = rich.panel.Panel.fit(
#     Columns([argstable, argstable]),
#     title="My Panel",
#     border_style="red",
#     title_align="left",
#     padding=(1, 2),
# )

# console.print(panel)
# import rich.live
# print(rich.__file__)
# # rich.print(Panel("Hello, [red]World!"))
# # parser.print_help()

# value = 0
# increment = 2**0
# mod = 2**(args.mod_bit-1)


# def update_table(table: rich.table.Table = rich.table.Table(), value = 0) -> rich.table.Table:
#    """Make a new table."""
#    table.add_row(
#       f'Dec: {value}',f'Hex: {hex(value)}',f'Bin: {bin(value)}'
#    )
#    return rich.align.Align.center(table)

# table = rich.table.Table()
# rich.align.Align.center(table)
# table.add_column("Decimal")
# table.add_column("Hexa")
# table.add_column("Binary")

# with rich.live.Live(rich.align.Align.center(update_table(table, value)), 
#                      refresh_per_second=1/args.delay, 
#                      transient=False) as live:
#    try:
#       while value < args.iterations:
#          time.sleep(args.delay)
#          value += increment

#          if value % mod == 0:

#             live.update(update_table(table, value))
#             # cprint(f'Dec : {value};  \tBin : {bin(value)};  \tHex : {hex(value)};  \tLog10 : {np.log10(value)}', 'blue')

#          if value == (2**63)-1: 
#             time.sleep(.5)
#       time.sleep(1)
#    except KeyboardInterrupt:
#       print('\n\nDone ...\n')



# import socket

# import builtins
# dprint((dir(builtins)))
# dprint(socket.socket(socket.AF_INET, socket.SOCK_STREAM), ptype = 1)
# print(dir(socket))

# array = [1, 2, 3, 4, 5]
# dprint(array)
      
# for item, val in vars(socket.socket).items():
#    if not item.startswith('__'):
#       print(f'{item} | {val}')

# for item, val in vars(parser).items():
#    if not item.startswith('__'):
#       print(f'{item} | {val}')

# for item, val in vars(rich).items():
#    if not item.startswith('_'):
#       print(f'{item}\t| {val}')
      
# rich.inspect(rich)
# rich.inspect(rich.console)


# from rich.console import Console
# from rich.text import Text
# from rich.progress import Progress
# from rich.table import Table
# from rich.markdown import Markdown
# from rich.live import Live
# from rich import inspect
# # Colored Text
# console = Console(record=True, width=70)
# console.print("[bold green]Hello, World![/bold green]")

# # Styled Text
# styled_text = Text("Hello, World!", style = 'bold italic red')
# # inspect(styled_text, methods = True)
# console.print(styled_text)

# # Progress Bar
# with Progress() as progress:
#     task = progress.add_task("[cyan]Processing...", total=100)
#     for i in range(100):
#         progress.update(task, advance=1)
#         # Your processing logic here

# # Table Display
# table = Table(show_header=True, header_style="bold magenta")
# table.add_column("Name", style="bold cyan", width=12)
# table.add_column("Age", style="bold cyan", width=8)
# table.add_row("John Doe", '30')
# table.add_row("Jane Smith", '25')
# console.print(table)

# # Syntax Highlighting
# code = "def hello():\n    print('Hello, Rich!')"
# console.print("[bold yellow]Python Code:[/bold yellow]\n")
# console.print(code, style="bold")

# # Markdown Rendering
# markdown_text = """
# # Rich Module

# `rich` is a Python library for rich text and beautiful formatting in the terminal.

# - Supports various text styles
# - Tables, progress bars, syntax highlighting, etc.

# """
# console.print(Markdown(markdown_text))

# # Link Formatting
# console.print("Check out the [link=https://github.com/willmcgugan/rich]Rich GitHub[/link] for more information.")

# table = Table("Name", "Styling")
# from rich.default_styles import DEFAULT_STYLES

# for style_name, style in DEFAULT_STYLES.items():
#    table.add_row(Text(style_name, style=style), str(style))
# console.print(table)

# inspect(Console, methods = True)
# inspect(Text, methods = True)
# inspect(Markdown, methods = True)
# inspect(Progress, methods = True)
# inspect(Live, methods = True)
# inspect(Table, methods = True)

import os
import threading
import time

def say(msg: str, voice: str = 'Samantha', rate: int = 160):
    threading.Thread(target=voice_cmd, name=None, args=(msg, voice, rate,)).start()

def voice_cmd(msg, voice, rate):
    os.system(f'say -v {voice} -r {rate} {msg}')
    
def notif(type: str = 'Blow'):
    threading.Thread(target=notif_cmd, name=None, args=(type,)).start()

def notif_cmd(type):
    os.system(f'afplay {os.path.dirname(__file__)}/richsockets/SoundLib/{type}.aiff')

### threaded (non-interrupting) sound widgets working

# say('Client connected')
# say('Client disconnected')
# say('Client rejected')
# say('Server closing')

from rich.console import Console
import time
console = Console(highlight = False)

for type in os.listdir('richsockets/SoundLib'):
    console.print(type)
    notif(type)
    inp = input()
    