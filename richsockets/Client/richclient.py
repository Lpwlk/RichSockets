#!/usr/bin/env python3

from richsockets.utils import *
import struct
import threading
import hashlib

class Client:
    ''' 
    Client object to be called after importing richsockets package.
    '''
    def __init__(self, host: str = socket.gethostbyname(socket.gethostname()), port: int = 8000, color: str = 'white', ID: str = hex(2**16-1),):
        # '''__init__ 
        # Self client attributes are defined after connection to remote 
        # hosts except port & ip addr required for connection.
        
        # Args:
        #     host (str, optional): remote server's IP adress. Defaults to socket.gethostbyname(socket.gethostname()).
        #     port (int, optional): TCP port number. Defaults to 8000.

        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.log = None
        self.logpath = None
        self.color = color
        self.ID = None

    def connect(self):
        '''Client.connect() 
        Client connection routine including logging init, authentification if
        remote server is in secured mode and attributes reception from host.
        Args:
            None
        '''
        self.client_socket.connect((self.host, self.port))
        self.ID = hex(np.random.randint(0,2**16-1))
        self.color = self.client_socket.recv(64).decode()
        self.client_socket.send(self.ID.encode())
        log_num = int(self.client_socket.recv(64).decode().split('°')[-1])
        self.log, self.logpath = init_client_log(log_num, verbose = 1)
        self.log.info(f'Client connected to server {self.client_socket.getpeername()}')
        bprint([f'Connected to server @ {self.client_socket.getsockname()[0]}', f'IPV4/port : {self.client_socket.getsockname()}'], color = 'light_green', box_color = 'green', width=35, size = (1,2))
        cprint(f'Client connection logs saved at: {self.logpath}', self.color)
        get_socket_details(self.client_socket, color = self.color, clientID = self.ID, verbose = 1)
    
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
        cprint(f'Client {self.client_socket.getsockname()} disconnected from server', 'red')
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
        if verbose: cprint(f'\tSending data to {self.client_socket.getpeername()} : {frame}', self.color)
        
    def receive(self, n_bytes = 1024, verbose = 1):
        '''receive _summary_

        Args:
            n_bytes (int, optional): _description_. Defaults to 1024.
            verbose (int, optional): _description_. Defaults to 1.

        Returns:
            _type_: _description_
        '''
        data = self.client_socket.recv(n_bytes)
        if verbose: cprint(f'\tReceived data from {self.client_socket.getpeername()} : {data}', self.color)
        return data 
    
    def check_sha(self, sent_frame, verbose = 0):
        '''check_sha _summary_

        Args:
            sent_frame (_type_): _description_
            verbose (int, optional): _description_. Defaults to 0.
        '''
        server_resp = self.client_socket.recv(256).decode()
        sha_256 = hashlib.sha256(sent_frame).hexdigest()
        cprint(f' > Locally computed SHA-256: \t{str(sha_256)[:40]}', color = self.color)
        if verbose:
            if sha_256 == server_resp:
                cprint(f' > Received SHA-256 from serv:  {server_resp[:40]}', 'green')
            else:
                cprint(f' > Received SHA-256 from serv:  {server_resp[:40]}', 'red')
                
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
        cprint(data, self.color)
        
    def get_sock_info(self):
        '''get_sock_info _summary_
        '''
        self.send('get_sock_details')
        data = self.client_socket.recv(1024).decode()
        now = datetime.now()
        cprint(f'Client connection logs saved at: {self.logpath}', self.color)
        bprint([f'{now.strftime("%m/%d/%y - %H:%M:%S")}', 'Client socket details',  f'16-bit ID: {self.ID}'], color = self.color, box_color = self.color, width = 21, size = (1, 3))
        cprint(data, self.color)
        
    def broadcast(self):
        '''broadcast _summary_
        '''
        self.send('broadcast')
        event = threading.Event()
        # client_name = input(' > Type pseudo for chat room : '); sys.stdout.write("\033[F"); sys.stdout.write("\033[K")
        client_name = f'{self.client_socket.getsockname()}'
        cprint('\n\t'+'-'*40 + f'\n\t > Entering chat room with pseudo : {client_name}', self.color)
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
        cprint(f'\t> Server CPU temp is {temp} °C', self.color)
    
    def ping_server(self):
        ''' Client.ping_server() 
        '''
        time.sleep(.1)
        t_ping = time.time()
        self.send('get_pong')
        pong = self.receive(verbose = 0)
        cprint(f'\t> {pong} received : took {round(1000*(time.time()-t_ping), 4)} ms', self.color)
    
    def send_file(self, sendpath: str = None, 
                  recv_name: str = None,  
                  buf_len: int = 4096): 
        '''send_file _summary_

        Args:
            sendpath (str, optional): _description_. Defaults to None.
            recv_name (str, optional): _description_. Defaults to None.
            buf_len (int, optional): _description_. Defaults to 4096.
        '''
        sendpath = valid_input(prompt = 'Type path from cwd to send :', input_trigger = sendpath)
        recv_name = valid_input(prompt = 'Type recv filename :', input_trigger = recv_name)
        filesize = os.path.getsize(sendpath)
        self.send(f'download,{filesize},{buf_len},{recv_name}')
        progress = tqdm(range(filesize), f"Sending file ", unit="B", unit_scale=True, unit_divisor=1024, colour = self.color, dynamic_ncols = True)
        with open(sendpath, 'rb') as f:
            while True:
                bytes_read = f.read(buf_len)
                if not bytes_read: break
                self.client_socket.send(bytes_read); progress.update(len(bytes_read))
            progress.close(); f.seek(0)
            sent_content = f.read()
            self.check_sha(sent_content, verbose = 1)
    
    def send_folder(self, sendpath: str = None, 
                    recv_name: str = None,  
                    buf_len: int = 4096):
        '''send_folder _summary_

        Args:
            sendpath (str, optional): _description_. Defaults to None.
            recv_name (str, optional): _description_. Defaults to None.
            buf_len (int, optional): _description_. Defaults to 4096.
        '''
        sendpath = valid_input(prompt = 'Type path from cwd to send :', input_trigger = sendpath)
        recv_name = valid_input(prompt = 'Type recv foldername :', input_trigger = recv_name)
        print(f'{os.listdir(sendpath)=}')
        print(f'{os.walk(sendpath)=}')
        if os.path.isdir(sendpath):
            for file in os.listdir(sendpath):
                print(file)
                if os.path.isdir(file):
                    self.send_folder(sendpath = os.path.join(sendpath, file), recv_name = file)
                    sendpath = file
                else:
                    filesize = os.path.getsize(file)
                    self.send(f'download,{filesize},{buf_len},{recv_name}')
                    progress = tqdm(range(filesize), f"Sending file ", unit="B", unit_scale=True, unit_divisor=1024, colour = self.color, dynamic_ncols = True)
                    with open(file, 'rb') as f:
                        while True:
                            bytes_read = f.read(buf_len)
                            if not bytes_read: break
                            self.client_socket.send(bytes_read); progress.update(len(bytes_read))
                        progress.close(); f.seek(0)
                        sent_content = f.read()
                        self.check_sha(sent_content, verbose = 1)
        else: print('Wrong path')
                    
    def stream_channel(self, channel: int = 3, delay: int = 200, buf_len: int = 4, n_packet: int = 0, save_txt: int = 1, verbose: int = 1):
        # channel = valid_input('Enter channel number > Ch n°', bounds = [1, 3], input_trigger = channel)
        # delay = valid_input('Enter serv side delay for streaming session (ms) > ', bounds = [1, 10000], input_trigger = delay)
        # buf_len = valid_input('Enter buffer_length for streaming session > ', bounds = [1, 64], input_trigger = buf_len)
        # n_packet = valid_input('Enter n_packet for streaming session > ', bounds = [0, 1e9], input_trigger = n_packet)
        # save_txt = valid_input('Enter 1 to save data in a txt file (save_txt flag) > ', bounds = [0, 1], input_trigger = save_txt)
        # verbose = valid_input('Enter 1 to display data in stdout (verbose flag) > ', bounds = [0, 1], input_trigger = verbose)
        channel_path =os.getcwd()+'/'+f'richsockets/Client/DataBase/StreamData/data_channel_{channel}.txt'
        with open(channel_path, mode = 'a') as f: 
            f.truncate(0); f.close()
            cprint(f'Stream save file : {channel_path} cleared', 'red')
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
                            cprint(f'{" ".join(map(str, content))}', self.color)
                        f.write(f'{" ".join(map(str, content))}\n')
                        f.close()
                stream_cnt += 1
                if  (stream_cnt == n_packet): # (n_packet != 0) and
                        cprint(f'Streaming on channel n°{channel} closed, {stream_cnt} packets received from {self.client_socket.getpeername()}', self.color)
                        break
            except KeyboardInterrupt:
                self.send('stop_streaming')
                cprint(f'Keyboard interrupt > streaming closed from client, {stream_cnt} packets received from {self.client_socket.getpeername()}', 'red')
                break
        cprint(f'Elapsed time in client streaming reception loop : {round((time.time()-t_start)*1000, 4)} ms', self.color)
