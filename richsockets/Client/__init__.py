from rich import print

print(f'__init__ traceback @ {__path__  = }\n\t\t{__name__ = }\n\t\t{__file__ = }\n\t\t{__loader__ = }\n\n {'──'*10}')

# from rich.prompt import Confirm
# is_rich_great = Confirm.ask("Do you like rich?")
# assert is_rich_great