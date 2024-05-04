#!/usr/bin/env python3
from richsockets.utils import *

class Client:
    def __init__(self, host: str = socket.gethostbyname(socket.gethostname()), port: int = 8000, color: str = 'white'):
        self.host: str = host
        self.port: int = port
        self.client_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.color: str = 'white'
        self.ID: str = None
        self.log: logging.Logger = None

    def run(self):
        try:
            if self.connect():
                while True:
                    cmd = self.get_command()
                    match cmd:
                        case 'h': client_help()
                        case 'p': self.ping_server()
                        case 't': self.get_temp()
                        case 'd': self.print_attrs()
                        case 'in': self.self_inspect()
                        case 'sd': self.send_file()
                        case 'cl': self.close()
                        case _ :
                            print('[bold red]Error: Command unknown, see client help (h cmd) for available commands ...') 
                            self.log.error('Unknown user input in client command loop') 
                            pass
                                        
            else: self.close()
        except KeyboardInterrupt:
            console.print('[bold red]Keyboard interrupt -> Client socket closing ...')
            self.close()
        
    def get_command(self):
        inp = Prompt.ask('[bold green]Client command', default = 'h', show_default=True)
        self.log.info(f'Client object received input command : {inp}')
        return inp
    
    def connect(self):
        self.client_socket.connect((self.host, self.port))
        self.ID, self.color, log_index = self.client_socket.recv(128).decode().split(',')
        self.log, self.logpath = init_client_log(log_index)
        if self.authentication():
            self.log.info(f'Client {self.client_socket.getpeername()} authentified to server')
            console.print(f'Connected to server @ {self.client_socket.getsockname()[0]} | IPV4/port : {self.client_socket.getsockname()}', style = 'green')
            get_socket_attrs(self.client_socket)
            return True
        else: 
            return False
            
    def authentication(self):
        if self.get_response() == ResponseCodes.NAUTH:
            console.print('[bold green]Server is not in secure mode, no authentification required ...')
            return True
        else:
            mode = Prompt.ask('[italic yellow]Would you login or register (or dev by-pass) ?', default = 'l', choices = ['l', 'r', 'b'], show_default=True, show_choices = True, console = console)
            if mode == 'l':
                self.send_request(RequestCodes.LOGIN)
                return self.login()
            elif mode == 'r':
                self.send_request(RequestCodes.REGISTER)
                return self.register()
            elif mode == 'b':
                self.send_request(RequestCodes.DEVBYPASS)
                return True
            
    def login(self):
        try:
            while True:
                username = Prompt.ask('[italic yellow]| Enter username:', console = console)
                password = sha256(Prompt.ask('[italic yellow]| Enter password:', password = True, console = console).encode())
                self.send(f'{username},{password}'.encode())
                server_status = self.get_response()
                if server_status == ResponseCodes.OK: 
                    return True
                elif server_status == ResponseCodes.NOK:
                    pass
                elif server_status == ResponseCodes.AUTHFAILED: 
                    console.print('Authentifiation failed because you reached server login limit')
                    return False
        except KeyboardInterrupt: 
            return False
              
    def register(self):
        try:
            username = Prompt.ask('[italic yellow]| Enter your new username:', console = console)
            password = sha256(Prompt.ask('[italic yellow]| Enter your new password:', password = True, console = console).encode())
            self.send(f'{username},{password}')
            return self.login()
        except KeyboardInterrupt: 
            return False
        
    def close(self):
        self.log.info('Client socket closing after sending disconnect request.')
        self.send_request(RequestCodes.DISCONNECT)
        handlers = self.log.handlers[:]
        for handler in handlers:
            self.log.removeHandler(handler)
            handler.close()
        console.print(f'Client {self.client_socket.getsockname()} disconnected from server', 'red')
        self.client_socket.close()

    def send(self, data: bytes, verbose: bool = 1):
        self.client_socket.send(data)
        self.log.info(f'Client sent : {data}')
        if verbose: 
            console.print(f'Sending data to {self.client_socket.getpeername()} : {data}', style = self.color)
    
    def receive(self, n_bytes = 512, verbose = 1):
        data = self.client_socket.recv(n_bytes)
        if verbose: 
            console.print(f'Received data from {self.client_socket.getpeername()} : {data}', style = self.color)
        return data 
    
    def send_request(self, request: RequestCodes, verbose: bool = False, log: bool = True) -> None:
        self.client_socket.send(request)
        if verbose: console.print(f'Sent request [bold]{translateRequest(request)}[/bold] to {self.client_socket.getpeername()}')
        if log: self.log.info(f'Sent request {translateRequest(request)} to {self.client_socket.getpeername()}')
        
    def get_response(self, verbose: bool = False, log: bool = True) -> bytes:
        response = self.client_socket.recv(2)
        if verbose: console.print(f'Received response [bold]{translateResponse(response)}[/bold] from {self.client_socket.getpeername()}')
        if log: self.log.info(f'Received response {translateResponse(response)} from {self.client_socket.getpeername()}')
        return response
    
    def check_sha(self, sent_frame, verbose = 0):
        server_resp = self.client_socket.recv(256).decode()
        sha_256 = hashlib.sha256(sent_frame).hexdigest()
        console.print(f' > Locally computed SHA-256: \t{str(sha_256)[:40]}', color = self.color)
        if verbose:
            if sha_256 == server_resp:
                console.print(f' > Received SHA-256 from serv:  {server_resp[:40]}', 'green')
            else:
                console.print(f' > Received SHA-256 from serv:  {server_resp[:40]}', 'red')
                
    def recv_thread(self, event):
        while not event.is_set():
            print('test')
            time.sleep(.1)
            data = self.client_socket.recv(512).decode()
            if '⎹' in data:
                print(f'{data}\n > ', end = '')
                
    def print_attrs(self):
        self.send_request(RequestCodes.ATTRS)
        get_socket_attrs(self.client_socket)
    
    def self_inspect(self):
        inspect(self)

    def ping_server(self):
        time.sleep(.1)
        t_ping = time.time()
        self.send_request(RequestCodes.PING)
        pong = self.receive(verbose = 0)
        console.print(f'{pong} received : took {round(1000*(time.time()-t_ping), 4)} ms', style = self.color)

    def get_temp(self):
        self.send_request(RequestCodes.TEMP)
        temp = float(self.receive())
        console.print(f'\t> Server CPU temp is {temp} °C', style = self.color)
        
    def shutdown_server(self):
        self.send_request(RequestCodes.SHUTDOWN)
        
