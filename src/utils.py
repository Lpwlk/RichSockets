from mytools import cprint

import os
import sys
import time
import socket
import logging
import platform
import mactemperatures
from tqdm import tqdm
from datetime import datetime
from mytools import bprint, cprint

# import shutil
# shutil.make_archive('test', 'zip', 'ServerDataBase')

def header():
    cprint(' '+'-'*60, 'yellow')
    cprint(f' ⎹ > Python script execution init ...', 'yellow', 'on_grey')
    cprint(f' ⎹ Node_name : {platform.uname().node} (OS {platform.uname().system})', 'yellow', 'on_grey')
    cprint(f' ⎹ Sys.argv : {sys.argv}', 'yellow', 'on_grey')
    cprint(f' ⎹ Location : {os.getcwd()}', 'yellow', 'on_grey', end = '\n\n')
    
def init_client_log(log_num, verbose = 0, stream=0):
    log_path = f'Client/DataBase/Logs/log_client_{log_num}.log'
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
    log_path = 'Server/DataBase/Logs/log_server.log'
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
    return socket.gethostbyname(socket.gethostname())

def fake_process(delay, res):
    time.sleep(.2)
    for _ in tqdm(range(res), desc = ' > Process ', dynamic_ncols = True): time.sleep(delay/res)
    
def get_cpu_temp():
    opsystem = platform.system()
    if opsystem == "Linux": 
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as file: 
            return float(file.read().strip()) / 1000.0
    elif opsystem == "Darwin": 
        return float(mactemperatures.get_thermal_readings()['PMU tdie1'])
def tree_recursive(chemin = os.getcwd(), ident = '', color = 'blue'):
    if os.path.isdir(chemin): 
        cprint(ident + os.path.basename(chemin) + '/', color); ident += '    '
        for element in os.listdir(chemin): 
            tree_recursive(os.path.join(chemin, element), ident)
    else: cprint(ident + os.path.basename(chemin), color)
    
def valid_input(prompt = 'User input > ', bounds = [1, 1000], input_trigger = None):
    if input_trigger == None:
        if isinstance(input_trigger, int):
            try:
                user_input = int(input(prompt))
            except Exception as e:
                user_input = int(input(f'Invalid input ({e}), ' + prompt))
            while not bounds[0] <= user_input <= bounds[1]: 
                try: 
                    user_input = int(input('Invalid input, ' + prompt))
                except Exception as e:
                    user_input = int(input(f'Invalid input ({e}), ' + prompt))
        elif isinstance(input_trigger, str): 
            try:
                user_input = str(input(prompt))
            except Exception as e:
                user_input = str(input(f'Invalid input ({e}), ' + prompt))
            while not bounds[0] < len(user_input) <= bounds[1]: 
                try: 
                    user_input = str(input('Invalid input, ' + prompt))
                except Exception as e:
                    user_input = str(input(f'Invalid input ({e}), ' + prompt))
        return user_input
    else:
        return input_trigger
                    
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
