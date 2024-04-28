# rich.traceback import @ package root for easy troobleshooting,makes traceback and errors appear 
# with colors & local variables values in a rich-powered panel. install function calls and installs a 
# traceback handler for every submodules which are called after this.
from rich.traceback import install  
install(width = 120, show_locals=True)

# from rich import print
# print(f'__init__ traceback @ {__path__  = }\n\t\t{__name__ = }\n\t\t{__file__ = }\n {'──'*50}')

