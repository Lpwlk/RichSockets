#!/usr/bin/env python3

import os
import time
import socket
import struct
import hashlib
import threading
from tqdm import tqdm
from datetime import datetime
from mytools import bprint, cprint
import numpy as np
import directory_tree as dtree
from src.utils import *
from rich.traceback import install
install(show_locals=True)
# import shutil
# shutil.make_archive('test', 'zip', 'Server/DataBase')

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.boot_time = time.time()
        self.log = init_server_log()

    def serve(self, n_clients):
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(n_clients)
        bprint([f'Server listening up to {n_clients} clients', f'IPV4/port : {self.server_socket.getsockname()}'], color = 'light_green', box_color = 'green', width=35, size = (1,2))
        self.log.info(f'Server listening up to {n_clients} clients on : {self.server_socket.getsockname()}')
        i, colors = 0, ['blue','green','yellow','magenta','white']

        while True:
            if i == n_clients: i = 1
            else: i += 1
            color = colors[i-1]
            try:
                client_socket, addr = self.server_socket.accept()
                cprint(f'\nNew connected client : {addr}', 'green')
                self.log.info(f'New connected client : {addr}')
                self.clients.append(client_socket)
                client_socket.send(color.encode())
                clientID = client_socket.recv(64).decode()
                client_socket.send(f'Log into client n°{i}'.encode())
                client_thread = threading.Thread(target = self.handle_client, args = (client_socket, color, clientID))
                cprint(f' └── Client thread {client_thread.name} started at {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}', 'green')
                client_thread.start()

            except KeyboardInterrupt:
                cprint('\t\nKeyboard interrupt -> server threader closed', 'red')
                for client in self.clients:
                    client.close()
                self.close()
                break

    def close(self):
        self.log.info('Keyboard interrupt -> server threading loop closed')
        cprint(f'Server started {round((time.time()-self.boot_time)/60, 2)} minutes ago')
        self.server_socket.close()
        
    def send(self, client_socket, data, color = 'yellow'):
        data = (f'{data}')
        cprint(f'\t> Server response to {client_socket.getpeername()} : {data}', color)
        client_socket.send(data.encode())
        
    def receive(self, client_socket, color):
        data = client_socket.recv(1024)
        cprint(f'\t> Received data from {client_socket.getpeername()} : {data}', color)
        return data
    
    def broadcast(self, client_socket, data: bytes, color):
        cprint(f'\t> Broadcasting data to every clients : {data.decode()}', color)
        for client in self.clients: 
            client.send(data)
            
    def get_request(self, client_socket: socket.socket, color):
        request = client_socket.recv(1024)
        cprint('\t'+'-'*60, color)
        cprint(f'\t> Received request from {client_socket.getpeername()} : {request}', color)
        self.log.info(f'Received request from {client_socket.getpeername()} : {request}')
        return request
    
    def send_sha(self, client_socket: socket.socket, data, color):
        sha_256 = hashlib.sha256(data).hexdigest()
        cprint(f' > Sending locally computed SHA-256 : {sha_256}', color)
        client_socket.send(f'{sha_256}'.encode())
        return sha_256
    
    def update_packet(self, channel, verbose, buf_len, cnt, color):
        if channel == 1:
            arr = np.random.randint(0, 1000, size = buf_len)
            packet = struct.pack(f'{buf_len}i', *arr)
        elif channel == 2:
            arr = np.random.normal(loc=0, scale=1, size = buf_len)
            for i in range(len(arr)): arr[i] = round(arr[i], 4)
            packet = struct.pack(f'{buf_len}d', *arr)
        elif channel == 3:
            x = np.linspace(cnt, cnt+1, buf_len)
            arr = [np.sin(i*cnt/100) for i in x]
            packet = struct.pack(f'{buf_len}d', *arr)
        if verbose: 
            cprint(" ".join(map(str, arr)),color)
        return packet
    
    def handle_client(self, client_socket, color, clientID):
        self.log.info(f' └── Client thread started for client {client_socket.getpeername()}')
        get_socket_details(client_socket, verbose = 1, color = color, clientID = clientID)
        while True:
            try:
                request = self.get_request(client_socket, color)
                if request == b'server_temp':
                    temp = get_cpu_temp()
                    self.send(client_socket, temp, color)
                if request == b'broadcast':
                    cprint(f' > Client {client_socket.getsockname()} entered the chat room', color)
                    broadcasted_data = client_socket.recv(1024)
                    while broadcasted_data != b'q':
                        self.broadcast(client_socket, broadcasted_data, color)
                        broadcasted_data = client_socket.recv(1024)
                        print(broadcasted_data)
                    cprint(f' > Client {client_socket.getpeername()} exited the chat room', color)
                if request == b'get_dbp':
                    # db_tree = dtree.display_tree(dir_path=os.getcwd(), string_rep=True, max_depth=float("inf"), show_hidden=True)
                    db_tree = dtree.display_tree(dir_path=os.path.join(os.getcwd(),'ServerDataBase', ''), string_rep=True, max_depth=float("inf"), show_hidden=True)
                    self.send(client_socket, db_tree, color)
                if request == b'get_sock_details':
                    sock_details = get_socket_details(client_socket, verbose = 1, color = color)
                    client_socket.send(sock_details.encode())

                if request == b'get_pong':
                    self.send(client_socket, 'pong', color)
                if request == b'disconnect' or request == b'':
                    self.clients.remove(client_socket)
                    cprint(f'Client {client_socket.getpeername()} disconnected from server ({len(self.clients)} clients connected now)', 'red')
                    self.log.info(f'Client {client_socket.getpeername()} disconnected from server ({len(self.clients)} clients connected now)')
                    self.log.info(f' ─── Client {client_socket.getpeername()} thread exited after disconnect request with code : 0')
                    client_socket.close()
                    break
                if request.startswith(b'download'):
                    dwnld_specs = request.split(b',')
                    filesize, buf_len, dwn_path = int(dwnld_specs[1]), int(dwnld_specs[2]), 'ServerDataBase/Downloads/'+dwnld_specs[3].decode()
                    progress = tqdm(range(filesize), f"Receiving file @ {dwn_path[14:]}", unit="B", unit_scale=True, unit_divisor=1024, colour = 'blue', dynamic_ncols = True)
                    with open(dwn_path, 'wb') as f:
                        n_bytes = 0
                        while n_bytes < filesize:
                            bytes_read = client_socket.recv(buf_len)
                            progress.update(len(bytes_read))
                            n_bytes += len(bytes_read)
                            f.write(bytes_read)
                        progress.close()
                    recv_content = open(dwn_path, 'rb').read()
                    self.send_sha(client_socket, recv_content, color)
                
                if request.startswith(b'stream'):
                    stream_specs = request.split(b',')
                    channel, buf_len, n_packet, verbose, delay = [int(stream_specs[i]) for i in range(1, 6)]
                    stream_cnt = 0
                    flag = 1
                    if n_packet == 0:                     
                        interrupt_thread = threading.Thread(target=client_socket.recv, args=(64,))
                        interrupt_thread.start()
                    t_start = time.time()
                    while flag:
                        data = self.update_packet(channel, verbose, buf_len, stream_cnt, color)
                        client_socket.send(data)
                        stream_cnt += 1
                        time.sleep(delay/1000)
                        if n_packet == 0: flag = interrupt_thread.is_alive()
                        else: flag = (stream_cnt != n_packet)

                    cprint(f'Data streaming on channel n°{channel} closed, {stream_cnt} packets have been sent to {client_socket.getpeername()}', color)
                    cprint(f'Elapsed time in server streaming loop : {round((time.time()-t_start), 6)} s', color)

            except Exception as e:
                self.clients.remove(client_socket)
                cprint(f'Client {client_socket.getsockname()} handling broken : {e} ({len(self.clients)} clients connected now)', 'red')
                self.log.error(f'Client {client_socket.getsockname()} handling broken ({len(self.clients)} clients connected now)', exc_info = 1)
                self.log.info(f' ─── Client {client_socket.getpeername()} thread exited after exception ({e}) with code : 0')
                client_socket.close()
                break