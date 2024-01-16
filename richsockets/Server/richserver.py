#!/usr/bin/env python3

from richsockets.utils import *
import struct
import threading
import hashlib

class Server:
    def __init__(self, host, port):
        '''Server() Server object to call after richsockets import. It includes a front-end
        cli interface based on the rich package & a socket back-end protocol. 
        All services are compatible with multiple Client object instance.


        Args:
            host (_type_): _description_
            port (_type_): _description_
        '''
        self.host: str = host
        self.port: int = port
        
        self.server_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.secure: bool = False
        self.clients: list = []
        self.boot_time: float = time.time()
        self.log: logging.Logger = init_server_log()
        
    def serve(self, max_client):
        # Setting up server for debug & loop tracking purposes
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Binding server to port & IPv4 adress provided in server instance call.
        self.server_socket.bind((self.host, self.port))
        # starting threading loop for incomming connection requests, automatic client socket disconnection in case of password error wih secure flag on.
        self.server_socket.listen(max_client)
        console.print(f'Server listening up to {max_client} clients   |   IPV4/port : {self.server_socket.getsockname()}', style = 'green')
        self.log.info(f'Server listening up to {max_client} clients on : {self.server_socket.getsockname()}')
        client_index, colors = 0, ['blue','green','yellow','magenta','white']

        while True:
            
            if client_index == max_client: 
                client_index = 1
            else: 
                client_index += 1
            
            try:
                
                # Blocking method for continuous listening of connection requests
                client_socket, addr = self.server_socket.accept()
                
                console.print(f'New connected client : {addr}', style = 'bold green')
                clientID = hex(np.random.randint(0,2**16-1))
                color = colors[client_index-1]
                # Sending
                client_socket.send(f'{clientID},{color},{client_index}'.encode())
                
                self.log.info(f'New connected client : {addr}')
                self.clients.append(client_socket)
                
                client_thread = threading.Thread(target = self.handle_client, args = (client_socket, color, clientID))
                console.print(f' └── Client thread {client_thread.name} started at {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}', style = 'green')
                client_thread.start()

            except KeyboardInterrupt:
                console.print('\t\nKeyboard interrupt -> server threader closed', style = 'red')
                for client in self.clients:
                    client.close()
                self.close()
                break

    def close(self):
        self.log.info('Keyboard interrupt -> server threading loop closed')
        console.print(f'Server started {round((time.time()-self.boot_time)/60, 2)} minutes ago')
        self.server_socket.close()
        
    def send(self, client_socket, data, color = 'yellow'):
        data = (f'{data}')
        console.print(f'\t> Server response to {client_socket.getpeername()} : {data}', style = color)
        client_socket.send(data.encode())
        
    def receive(self, client_socket, color):
        data = client_socket.recv(1024)
        console.print(f'\t> Received data from {client_socket.getpeername()} : {data}', style = color)
        return data
    
    def broadcast(self, client_socket, data: bytes, color):
        console.print(f'\t> Broadcasting data to every clients : {data.decode()}', style = color)
        for client in self.clients: 
            client.send(data)
            
    def get_request(self, client_socket: socket.socket, color):
        request = client_socket.recv(1024)
        console.print('\t'+'-'*60, style = color)
        console.print(f'\tReceived request from {client_socket.getpeername()} : {request}', style = color)
        self.log.info(f'Received request from {client_socket.getpeername()} : {request}')
        return request
    
    def send_sha(self, client_socket: socket.socket, data, color):
        sha_256 = hashlib.sha256(data).hexdigest()
        console.print(f' > Sending locally computed SHA-256 : {sha_256}', style = color)
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
            console.print(" ".join(map(str, arr)), style = color)
        return packet
    
    def handle_client(self, client_socket, color, clientID):
        
        self.log.info(f' └── Client thread started for client {client_socket.getpeername()}')
        get_client_details(client_socket, verbose = 1)

        while True:
            try:
                
                request = self.get_request(client_socket, color)
                match request:
                    case b'disconnect' | b'':
                        self.clients.remove(client_socket)
                        console.print(f'Client {client_socket.getpeername()} disconnected from server ({len(self.clients)} clients connected now)', style = 'red')
                        self.log.info(f'Client {client_socket.getpeername()} disconnected from server ({len(self.clients)} clients connected now)')
                        self.log.info(f' ─── Client {client_socket.getpeername()} thread exited after disconnect request with code : 0')
                        client_socket.close()
                        break
                    case b'get_pong': 
                        self.send(client_socket, 'pong', color)
                    case b'server_temp': 
                        self.send(client_socket, get_cpu_temp(), color)
                    case b'get_sock_details':
                        sock_details = get_client_details(client_socket, verbose = 1)
                        client_socket.send(sock_details.encode())
                    case b'get_dbp':
                        # db_tree = dtree.display_tree(dir_path=os.getcwd(), string_rep=True, max_depth=float("inf"), show_hidden=True)
                        # self.send(client_socket, db_tree, color)
                        pass
                    case b'broadcast':
                        console.print(f' > Client {client_socket.getsockname()} entered the chat room', style = color)
                        broadcasted_data = client_socket.recv(1024)
                        while broadcasted_data != b'q':
                            self.broadcast(client_socket, broadcasted_data, color)
                            broadcasted_data = client_socket.recv(1024)
                            console.print(broadcasted_data)
                        console.print(f' > Client {client_socket.getpeername()} exited the chat room', style = color)
                    case b'download':
                        dwnld_specs = request.split(b',')
                        filesize, buf_len, dwn_path = int(dwnld_specs[1]), int(dwnld_specs[2]), 'ServerDataBase/Downloads/'+dwnld_specs[3].decode()
                        with open(dwn_path, 'wb') as f:
                            n_bytes = 0
                            while n_bytes < filesize:
                                bytes_read = client_socket.recv(buf_len)
                                n_bytes += len(bytes_read)
                                f.write(bytes_read)
                        recv_content = open(dwn_path, 'rb').read()
                        self.send_sha(client_socket, recv_content, color)
                    case b'stream':
                        stream_specs = request.split(b',')
                        channel, buf_len, n_packet, verbose, delay = [int(stream_specs[i]) for i in range(1, len(stream_specs)-1)]
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
                        console.print(f'Data streaming on channel n°{channel} closed, {stream_cnt} packets have been sent to {client_socket.getpeername()}', style = color)
                        console.print(f'Elapsed time in server streaming loop : {round((time.time()-t_start), 6)} s', style = color)

                    case _ :
                        console.print('Unknown request received', style = 'bold red')
                process(5, 1000)
                # match request end
                        
            except Exception as e:
                
                self.clients.remove(client_socket)
                console.print(f'Client {client_socket.getsockname()} handling broken : {e} ({len(self.clients)} clients connected now)', style = 'red')
                self.log.error(f'Client {client_socket.getsockname()} handling broken ({len(self.clients)} clients connected now)', exc_info = 1)
                self.log.info(f' ─── Client {client_socket.getpeername()} thread exited after exception ({e}) with code : 0')
                client_socket.close()
                break