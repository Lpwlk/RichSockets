#!/usr/bin/env python3
from richsockets.utils import *

class Client:
    def __init__(self, socket: socket.socket, addr: str, index: int):
        self.socket = socket
        self.addr = addr
        self.index = index
        self.color = server_colors[self.index - 1]
        self.ID = hex(random.randint(0,2**16-1))
        self.username = f'invited n°{index}'
        self.send_client_frame()
        
    def send_client_frame(self):
        self.socket.send(f'{self.ID},{self.color},{self.index}'.encode())
    
class Server:
    def __init__(self, host, port, auth: bool = False):
        self.host: str = host
        self.port: int = port
        self.server_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.boot_time: float = time.time()
        self.auth: bool = auth
        self.attempts: int = 3
        self.clients: list = []
        self.client_index: int = 0
        self.log: logging.Logger = init_server_log()
        self.panel: Panel = Panel(' ', title=f'[blue]Connected clients: {len(self.clients)} | Time since server boot: {int((time.time()-self.boot_time)//3600)}:{int((time.time()-self.boot_time)//60)}:{(time.time()-self.boot_time)%60:.2f}[/blue]', subtitle=f'{self.host}:{self.port}')

    def footer(self):
        with Live(self.panel, console = console, refresh_per_second=20):
            while self.client_index != -1:
                self.panel.title = f'[blue]Connected clients: {len(self.clients)} | Time since server boot: {int((time.time()-self.boot_time)//3600)}:{int((time.time()-self.boot_time)//60)}:{(time.time()-self.boot_time)%60:.2f}[/blue]'

    def serve(self, max_client):
        footer_thread = threading.Thread(target = self.footer); footer_thread.start()
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(max_client)
        console.print(f'Server listening up to {max_client} clients | IPV4/port : {self.server_socket.getsockname()}', style = 'green')
        self.log.info(f'Server listening up to {max_client} clients | IPV4/port : {self.server_socket.getsockname()}')
        
        while True:
            try:
                client_socket, addr = self.server_socket.accept()
                self.log.info(f'New connected client : {addr}')
                
                if self.client_index == max_client: self.client_index = 1
                else: self.client_index += 1
                
                client = Client(client_socket, addr, self.client_index)
                self.clients.append(client)
                
                client_thread = threading.Thread(target = self.handle_client, args = (client,))
                console.print(f' └── Client {client_thread.name} started at {get_time()}', style = 'green')
                self.log.info(f' └── Client thread started for client {client_socket.getpeername()}')
                client_thread.start()
                # get_threading_table()
            
            except KeyboardInterrupt:
                console.print('\nKeyboard interrupt -> server threader closed', style = 'bold red')
                self.close()
                self.client_index = -1
                sys.exit()
    
    def handle_connection_request(self, client):
        if not self.auth:
            self.send_response(client.socket, ResponseCodes.NAUTH)
            console.print(f'New connected client : {client.addr}', style = 'bold green')
            return True
        elif self.authentication(client): 
            console.print(f'Client authentified : socket {client.addr} connected', style = 'bold green')
            return True
        else: 
            console.print('Client authentification failed, socket closed', style = 'bold red')
            return False
            
    def authentication(self, client):
        self.send_response(client.socket, ResponseCodes.AUTH)
        
        auth_mode = self.get_request(client.socket)
        if auth_mode == RequestCodes.LOGIN:
            return self.login(client)
        elif auth_mode == RequestCodes.REGISTER:
            return self.register(client.socket)
        elif auth_mode == RequestCodes.DEVBYPASS:
            return True
        elif auth_mode == RequestCodes.DISCONNECT:
            console.print('test')
        
    def login(self, client):
        attempt = 0
        while True:
            attempt += 1
            console.print(f'attempt n°{attempt}/{self.attempts}')
            client_logs = client.socket.recv(128).decode()
            if client_logs == RequestCodes.DISCONNECT.decode():
                self.send_response(client.socket, ResponseCodes.AUTHFAILED); return False
            else:
                if self.check_logs(client_logs): 
                    self.send_response(client.socket, ResponseCodes.OK); return True
                elif attempt == self.attempts: 
                    self.send_response(client.socket, ResponseCodes.AUTHFAILED); return False
                else:
                    self.send_response(client.socket, ResponseCodes.NOK)

    def register(self, client):
        client_logs = client.socket.recv(128).decode()
        console.print(client_logs)
        with open(os.path.dirname(os.path.abspath(__file__))+'/DataBase/users_logs.txt', 'a') as f:
            f.write(client_logs + '\n')
        return self.login(client.socket)

    def check_logs(self, client_logs):
        with open(os.path.dirname(os.path.abspath(__file__))+'/DataBase/users_logs.txt', 'r') as f:
            logs_list = f.readlines()
            for logs in logs_list:
                if logs[:-1] == client_logs: return True
                else: console.print('Wrong login informations given', style = 'bold red'); return False
    
    def send_response(self, client_socket: socket.socket, response: ResponseCodes, verbose: bool = False, log: bool = True) -> None:
        client_socket.send(response)
        if verbose: console.print(f'Sent response [bold]{translateResponse(response)}[/bold] to {client_socket.getpeername()}')
        if log: self.log.info(f'Sent response {translateResponse(response)} to {client_socket.getpeername()}')

    def get_request(self, client_socket: socket.socket, verbose: bool = False, log: bool = True) -> bytes:
        request = client_socket.recv(2)
        if verbose: console.print(f'Received request [bold]{translateRequest(request)}[/bold] from {client_socket.getpeername()}')
        if log: self.log.info(f'Received request {translateRequest(request)} from {client_socket.getpeername()}')
        return request
            
    def handle_request(self, client_socket: socket.socket, verbose: bool = False, log: bool = True):
        request = self.get_request(client_socket)
        if b'10'<=request<=b'80':
            if verbose: console.print(f'Request accepted', style = 'green')
            if log: self.log.info(f'Request accepted')
        else:
            if verbose: console.print('Request denied', style = 'red')
            if log: self.log.info('Request denied')
        return request

    def remove_client(self, client):
        self.clients.remove(client)
        inspect(client.socket)
        console.print(f'Client {client.socket.getpeername()} disconnected from server ({len(self.clients)} clients connected now)', style = 'red')
        self.log.info(f'Client {client.socket.getpeername()} disconnected from server ({len(self.clients)} clients connected now)')
        self.log.info(f' ─── Client {client.socket.getpeername()} thread exited after disconnect request with code : 0')
        client.socket.close()
    
    def handle_client(self, client):
        if self.handle_connection_request(client):
            while True:
                request = self.handle_request(client.socket)
                match request:    
                    case RequestCodes.PING: 
                        self.send(client.socket, 'pong', client.color)
                    case RequestCodes.TEMP: 
                        self.send(client.socket, get_cpu_temp(), client.color)
                    case RequestCodes.ATTRS:
                        get_socket_attrs(client.socket)
                    case RequestCodes.DISCONNECT:
                        self.remove_client(client)
                        break
                    case RequestCodes.SHUTDOWN:
                        console.print(f'Received shutdown request from client {client.socket.getpeername()}  ({len(self.clients)}, server shuting down', style = 'bold red')
                        self.log.info(f'Received shutdown request from client {client.socket.getpeername()}  ({len(self.clients)}, server shuting down')
                        self.server_socket.close()
                        break
                    case _ :
                        console.print('Unknown request received', style = 'bold red')
        else: return False
        
    def close(self):
        console.print(f'Server up during {int((time.time()-self.boot_time)//3600)}:{int((time.time()-self.boot_time)//60)}:{(time.time()-self.boot_time)%60:.2f}')
        self.server_socket.close()

    def send(self, client_socket, data, color = 'yellow'):
        data = (f'{data}')
        console.print(f'Server response to {client_socket.getpeername()} : {data}', style = color)
        client_socket.send(data.encode())
        
    def receive(self, client_socket: socket.socket, n_bytes: int = 256, color: str = 'white'):
        data = client_socket.recv(n_bytes).decode()
        console.print(f'Received data from {client_socket.getpeername()} : {data}', style = color)
        return data
    
    def broadcast(self, client_socket, data: bytes, color):
        console.print(f'Broadcasting data to every clients : {data.decode()}', style = color)
        for client in self.clients: 
            client.send(data)
    