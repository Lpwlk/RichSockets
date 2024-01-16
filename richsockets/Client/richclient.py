#!/usr/bin/env python3

from richsockets.utils import *
import struct
import threading
import hashlib
from rich.prompt import Prompt

class Client:
    
    def __init__(self, host: str = socket.gethostbyname(socket.gethostname()), port: int = 8000, color: str = 'white', ID: str = hex(2**16-1)):
        
        '''Client() Client object to call after richsockets import. It includes a front-end
                    cli interface based on the rich package & a socket back-end protocol. 
                    All commands are compatible with a Server object instance.

        Args:
            host (str, optional): _description_. Defaults to socket.gethostbyname(socket.gethostname()).
            port (int, optional): _description_. Defaults to 8000.
            color (str, optional): _description_. Defaults to 'white'.
            ID (str, optional): _description_. Defaults to hex(2**16-1).
        '''
        self.host: str = host
        self.port: int = port
        self.client_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.color: str= None
        self.ID: str = None
        self.log  = None
        self.logpath = 'white'

    def get_command(self):
        inp = Prompt.ask('[bold green]Client command', default = 'h', show_default=False)
        self.log.info(f'Client object received input command : {inp}')
        return inp
    
    def connect(self):
        '''Client.connect() 
        Client connection routine including logging init, authentification if
        remote server is in secured mode and attributes reception from host.
        Args:
            None
        '''
        # Sending connection request to targeted host
        self.client_socket.connect((self.host, self.port))
        
        # reception of hex 16bit-ID, color and log_index from server right after reception
        recv_param = self.client_socket.recv(128).decode().split(',')
        self.ID, self.color, log_index = recv_param[0], recv_param[1], recv_param[2]
        
        # Starting logging handlers and
        self.log, self.logpath = init_client_log(log_index, verbose = 1)
        self.log.info(f'Client connected to server {self.client_socket.getpeername()}')
        console.print(f'Connected to server @ {self.client_socket.getsockname()[0]}   |   IPV4/port : {self.client_socket.getsockname()}', style = 'green')
        
        get_client_details(self.client_socket, verbose = 0)
        
    def close(self):
        '''Client.close() 
        Client disconnect routine: closing logging handlers and 
        sending disconnect request to current host.
        Args:
            None
        '''
        self.log.info('Client socket closing after sending disconnect request.')
        self.send('disconnect')
        handlers = self.log.handlers[:]
        for handler in handlers:
            self.log.removeHandler(handler)
            handler.close()
        console.print(f'Client {self.client_socket.getsockname()} disconnected from server', 'red')
        self.client_socket.close()
        
    def send(self, 
             data,
             verbose = 1):
        '''send Send routine, Deprecated, prefer to use directly self.client_socket.send(_.encode())

        Args:
            data (_type_): _description_
            verbose (int, optional): _description_. Defaults to 1.
        '''
        frame = f'{data}'
        self.client_socket.send(frame.encode())
        self.log.info(f'Client sent : {frame}')
        if verbose: console.print(f'\tSending data to {self.client_socket.getpeername()} : {frame}', style = self.color)
        
    def receive(self, n_bytes = 1024, verbose = 1):
        '''receive _summary_

        Args:
            n_bytes (int, optional): _description_. Defaults to 1024.
            verbose (int, optional): _description_. Defaults to 1.

        Returns:
            _type_: _description_
        '''
        data = self.client_socket.recv(n_bytes)
        if verbose: console.print(f'\tReceived data from {self.client_socket.getpeername()} : {data}', style = self.color)
        return data 
    
    def check_sha(self, sent_frame, verbose = 0):
        '''check_sha _summary_

        Args:
            sent_frame (_type_): _description_
            verbose (int, optional): _description_. Defaults to 0.
        '''
        server_resp = self.client_socket.recv(256).decode()
        sha_256 = hashlib.sha256(sent_frame).hexdigest()
        console.print(f' > Locally computed SHA-256: \t{str(sha_256)[:40]}', color = self.color)
        if verbose:
            if sha_256 == server_resp:
                console.print(f' > Received SHA-256 from serv:  {server_resp[:40]}', 'green')
            else:
                console.print(f' > Received SHA-256 from serv:  {server_resp[:40]}', 'red')
                
    def recv_thread(self, event):
        '''recv_thread _summary_

        Args:
            event (_type_): _description_
        '''
        while not event.is_set():
            print('test')
            time.sleep(.1)
            data = self.client_socket.recv(512).decode()
            if '⎹' in data:
                print(f'{data}\n > ', end = '')
                
    def get_dbp(self):
        '''get_dbp _summary_
        '''
        self.send('get_dbp', verbose = 0)
        data = self.receive(verbose = 0).decode()
        console.print(data, style = self.color)
        
    def get_sock_info(self):
        '''get_sock_info _summary_
        '''
        self.send('get_sock_details')
        data = self.client_socket.recv(1024).decode()
        now = datetime.now()
        console.print(f'Client connection logs saved at: {self.logpath}', style = self.color)
        console.print([f'{now.strftime("%m/%d/%y - %H:%M:%S")}  |  Client socket details  |  16-bit ID: {self.ID}'], style = self.color)
        console.print(data, style = self.color)
        
    def broadcast(self):
        '''broadcast _summary_
        '''
        self.send('broadcast')
        event = threading.Event()
        # client_name = input(' > Type pseudo for chat room : '); sys.stdout.write("\033[F"); sys.stdout.write("\033[K")
        client_name = f'{self.client_socket.getsockname()}'
        console.print('\n\t'+'-'*40 + f'\n\t > Entering chat room with pseudo : {client_name}', style = self.color)
        # recv_thread = threading.Thread(target=self.recv_thread, args=(event,))
        # recv_thread.start()
        msg = input(' > '); 
        sys.stdout.write("\033[F"); sys.stdout.write("\033[K")
        while msg != 'q':
            self.client_socket.send(f'{datetime.now().strftime("%H:%M:%S")} ⎹ {client_name} : {msg}'.encode())
            data = self.client_socket.recv(512).decode()
            print(f'{data}\n', end = '')
            msg = input(' > '); sys.stdout.write("\033[F"); sys.stdout.write("\033[K")
        self.client_socket.send(msg.encode())
    
    def get_temp(self):
        '''Client.get_temp() 
        '''
        self.send('server_temp')
        temp = float(self.receive())
        console.print(f'\t> Server CPU temp is {temp} °C', style = self.color)
    
    def ping_server(self):
        ''' Client.ping_server() 
        '''
        time.sleep(.1)
        t_ping = time.time()
        self.send('get_pong')
        pong = self.receive(verbose = 0)
        console.print(f'\t> {pong} received : took {round(1000*(time.time()-t_ping), 4)} ms', style = self.color)

    def stream_channel(self, channel: int = 3, delay: int = 200, buf_len: int = 4, n_packet: int = 0, save_txt: int = 1, verbose: int = 1):
        channel_path =os.getcwd()+'/'+f'richsockets/Client/DataBase/StreamData/data_channel_{channel}.txt'
        with open(channel_path, mode = 'a') as f: 
            f.truncate(0); f.close()
            console.print(f'Stream save file : {channel_path} cleared', style = 'red')
        self.send(f'stream,{channel},{buf_len},{n_packet},{verbose},{delay}')
        stream_cnt, t_start = 0, time.time()
        while True:
            try:
                if channel == 1:
                    content = struct.unpack(f'{buf_len}i', self.client_socket.recv(4*buf_len))
                elif channel == 2 or channel == 3:
                    content = struct.unpack(f'{buf_len}d', self.client_socket.recv(8*buf_len))

                if save_txt: 
                    with open(channel_path, mode = 'a') as f:
                        if verbose: 
                            console.print(f'{" ".join(map(str, content))}', style = self.color)
                        f.write(f'{" ".join(map(str, content))}\n')
                        f.close()
                stream_cnt += 1
                if  (stream_cnt == n_packet): # (n_packet != 0) and
                        console.print(f'Streaming on channel n°{channel} closed, {stream_cnt} packets received from {self.client_socket.getpeername()}', style = self.color)
                        break
            except KeyboardInterrupt:
                self.send('stop_streaming')
                console.print(f'Keyboard interrupt > streaming closed from client, {stream_cnt} packets received from {self.client_socket.getpeername()}', style = 'red')
                break
        console.print(f'Elapsed time in client streaming reception loop : {round((time.time()-t_start)*1000, 4)} ms', style = self.color)
