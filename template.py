import time 
from rich import print, inspect
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.align import Align
from rich.live import Live
from rich.theme import Theme
from rich.columns import Columns
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, Spinner

theme = Theme()
console = Console()

def init_server_ui(arg1: None = None, arg2: None = None):
    '''init_server_layout _summary_
    Args:
        arg1 (None, optional): _description_. Defaults to None.
        arg2 (None, optional): _description_. Defaults to None.
    '''
    
    layout = Layout() # init layout root component, sublayouts positions and sizes can be edited in this function 

    # split layout into 3 horizontal sublayouts: header, body and footer 
    layout.split_column(Layout(name ='header', ratio = 4), Layout(name ='body', ratio = 12), Layout(name ='footer', ratio = 2),)

    # split header and footer sublayouts in two columns (left and right for each component)
    layout['header'].split_row(Layout(name = 'lhead'), Layout(name = 'rhead'))
    layout['footer'].split_row(Layout(name = 'lfoot'), Layout(name = 'rfoot'))
    
    # split right header to display date & hour at the top and key info at the bottom
    layout['rhead'].split_column(Layout(name = 'trhead'), Layout(name = 'brhead'))
    
    # split body sublayout in three columns (left, main and right)
    layout['body'].split_row(Layout(name = 'lside', ratio = 3), Layout(name = 'main', ratio = 12), Layout(name = 'rside', ratio = 4))

    # split only left body sublayouts into three rows (top, middle and bottom)
    layout['lside'].split_column(Layout(name = 'ltop', ratio = 1), Layout(name = 'lmiddle', ratio = 1), Layout(name = 'lbottom', ratio = 1))

    return layout

def base_layout_arch(arg1: None = None, arg2: None = None):
    '''init_server_layout _summary_

    Args:
        arg1 (None, optional): _description_. Defaults to None.
        arg2 (None, optional): _description_. Defaults to None.
    '''
    
    layout = Layout(size = 10) # init the layout root component, sublayouts positions and sizes can be modified in this function 

    # split layout into 3 horizontal sublayouts: header, body and footer 
    layout.split_column(Layout(name ='header', ratio = 4), Layout(name ='body', ratio = 12), Layout(name ='footer', ratio = 3),)

    # split header and footer sublayouts in two columns (left and right for each component)
    layout['header'].split_row(Layout(name = 'lhead'), Layout(name = 'rhead'))
    layout['footer'].split_row(Layout(name = 'lfoot'), Layout(name = 'rfoot'))
    
    # split body sublayout in three columns (left, main and right)
    layout['body'].split_row(Layout(name = 'lside', ratio = 3), Layout(name = 'main', ratio = 12), Layout(name = 'rside', ratio = 4))
    
    # split left and right body sublayouts into three rows (top, middle and bottom)
    layout['rside'].split_column(Layout(name = 'rtop', ratio = 1), Layout(name = 'rmiddle', ratio = 1), Layout(name = 'rbottom', ratio = 1),)
    layout['lside'].split_column(Layout(name = 'ltop', ratio = 1), Layout(name = 'lmiddle', ratio = 1), Layout(name = 'lbottom', ratio = 1))

    return layout

prog = Progress(
    '{task.description}',
    SpinnerColumn(),
    BarColumn(),
    TextColumn('[progress.percentage]{task.percentage:>3.0f}%'),
)

layout = init_server_ui()
layout['lmiddle'].update(Align(Panel(layout['lside'].tree), align = 'center'))
layout['lbottom'].update(Align(prog, align = 'center'))
layout['rfoot'].update(Align(prog, align = 'center'))

task1 = prog.add_task('Yapa', total = 85)
task2 = prog.add_task('De', total = 75)
task3 = prog.add_task('Pano', total = 90)

i = 0
lps = 30
with Live(
    renderable = layout, 
    console = console,
    refresh_per_second = 4, 
    screen = False,
) as live:
    t_start = prog.get_time()
    while True:
        while not prog.finished:
            time.sleep(1.00/lps)
            for job in prog.tasks:
                if not job.finished:
                    prog.advance(job.id)
        i+=1
        layout['main'].update(Align(Panel(f'Time elapsed during process {round(prog.get_time()-t_start, 3)}'), align ='center'))
        live.console.print('test')
        for job in prog.tasks: prog.reset(job.id)