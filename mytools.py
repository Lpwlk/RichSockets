from termcolor import cprint
import textwrap
from typing import Literal
from inspect import getmembers

Attribute = Literal[
    "bold", "dark",
    "underline", "blink",
    "reverse", "concealed",
]

Highlight = Literal["on_black",         "on_white",
    "on_grey",      "on_light_grey",    "on_dark_grey",
    "on_red",       "on_light_red",
    "on_green",     "on_light_green",
    "on_yellow",    "on_light_yellow",
    "on_blue",      "on_light_blue",
    "on_magenta",   "on_light_magenta",
    "on_cyan",      "on_light_cyan",
]

Color = Literal[    "black",            "white",
    "grey",         "light_grey",       "dark_grey",
    "red",          "light_red",
    "green",        "light_green",
    "yellow",       "light_yellow",
    "blue",         "light_blue",
    "magenta",      "light_magenta",
    "cyan",         "light_cyan",
]


mt_tlc, mt_trc, mt_blc, mt_brc = '┌', '┐', '└', '┘'
mt_lsep, mt_rsep, mt_tsep, mt_bsep, mt_msep = '├', '┤', '┬', '┴', '┼'
mt_vline, mt_hline = '─', '│'
boxcomponents = '┌ ┐ └ ┘ ─ │ ┬ ┴ ├ ┤'

def bprint(
    text: list = ['Mono Boxprint element'], 
    box_color: Color = 'white', 
    color: Color = 'white', 
    size: tuple = (1,1), 
    width: int = 70, 
    hspace: int = 1,
    ) -> None:
    '''bprint Prints the given string list in an array of the given 
    shape. Function includes independant box & text color control as
    well as for the cells width and hspace for centered strings.
    
    Does not accept **kwargs for cprint calls

    Args:
        text (list, optional): String list input. Defaults to ['Mono Boxprint element'].
        box_color (Color, optional): Box color. Defaults to 'white'.
        color (Color, optional): text color. Defaults to 'white'.
        size (tuple, optional): Array output shape. Defaults to (1,1).
        width (int, optional): cell width. Defaults to 70.
        hspace (int, optional): cell hspace. Defaults to 1.
    '''
    rows, cols, wrapped, mono = size[0], size[1], [], True
    if len(text) > 1: mono = False
    for text in text: 
        wrap = textwrap.wrap(text = text, width = width)
        wrapped.append(wrap)
    maxline = max([len(i) for i in wrapped])
    if not mono:
        for row in range(rows):
            if row == 0: cprint(mt_tlc + (2*hspace+width)*mt_vline + (mt_tsep+(2*hspace+width)*mt_vline)*(cols-1) + mt_trc, box_color)
            else: cprint(mt_lsep + (2*hspace+width)*mt_vline + (mt_msep+(2*hspace+width)*mt_vline)*(cols-1) + mt_rsep, box_color)
            for line in range(maxline):
                for col in range(cols):
                    try:
                        cprint(mt_hline + hspace*' ', box_color, end = '')
                        cprint(wrapped[cols*row + col][line].center(width) + hspace*' ', color, end = ''); 
                        if col == cols-1:
                            cprint(mt_hline, box_color)
                    except IndexError as e:
                        cprint(' '.ljust(width) + hspace*' ', color, end = ''); 
                        if col == cols-1:
                            cprint(mt_hline, box_color)
            if row == rows-1: cprint(mt_blc + (2*hspace+width)*mt_vline + (mt_bsep+(2*hspace+width)*mt_vline)*(cols-1) + mt_brc, box_color)
    else:
        if len(text) > width : width = len(text)
        cprint(mt_tlc + (2*hspace+width)*mt_vline + mt_trc, box_color)
        cprint(mt_hline + hspace*' ', box_color, end = ''); cprint(text.center(width), color, end = ''); cprint(hspace*' ' + mt_hline, box_color);
        cprint(mt_blc + (2*hspace+width)*mt_vline + mt_brc, box_color)

def dprint(
    var: object | None = 'Debug',
    ptype: int | bool = False,
    color: Color | None = 'green',
    **kwargs
    ) -> None:
    '''dprint Debug print utlity, prints variables
    value and includes cprint and print argument

    Does accept **kwargs for cprint call
    
    Args:
        var (object | None, optional): Variable to debug. Defaults to 'Debug'.
        ptype (int | bool, optional): Type print flag. Defaults to False.
        color (Color | None, optional): Color for debug print. Defaults to 'green'.
    '''
    cprint(f'🪲  dprint call for {var = }', color)
    str = f'{var = }'
    if ptype:
        str += f' | {type(var) = }'
    cprint(text = str, color = color,  **kwargs)
    for attr, value in getmembers(var):
        if not attr.startswith(('_')):
            cprint(text = f'{attr}  ->  {value}', color = color,  **kwargs)
        else: pass




















# t1 = 'Text 1'
# t2 = 'Text 2'
# t3 = 'Myserver client side script to interract with the socket server structure in MyServer. Any available command to interract with the server is provided in the CLI help utility to be invoked using h cmd ...'
# t3cut = 'Myserver client side script to interract with the socket server structure in MyServer. Any available command to interract with the.'
# arr = [t3cut for _ in range(6)]
# bprint(text = [t1], size = (1,1))
# bprint(text = arr, size = (3,2), width = 40)
# for i in range(3):
#     arr[i] = 'Test'; 
#     if i == 2 : del arr[i]
# bprint(text = arr, size = (3,2), width = 75)
# bprint(text =[t3cut for _ in range(6)], box_color = 'blue', color = 'white', width = 90, hspace = 2, size = (3,2))
# bprint()
