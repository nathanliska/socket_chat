import socket
#from threading import Thread
from concurrent.futures import ThreadPoolExecutor

SERVER_ADDRESS = 'localhost'
SERVER_PORT = 8170
REQUESTS = 10
MESSAGE_SIZE = 2048


class Client:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.address = (self.ip, self.port)
        self.client = None

    def send_msg(self):
        while True:
            data = input("").encode()
            try:
                self.client.send(data)
            except ConnectionError as e:
                print("Connection closed!")
                break

    def run(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect(self.address)
        except socket.error as e:
            print(f"Cannot connect to server: {self.ip}:{self.port} {e}")
            exit(-1)

        executor = ThreadPoolExecutor(REQUESTS)
        executor.submit(self.send_msg)

        #input_thread = Thread(target=self.send_msg)
        #input_thread.start()

        while True:
            data = None
            try:
                data = self.client.recv(MESSAGE_SIZE)
            except ConnectionError as e:
                print(f"Connection closed! {e}")

            if data:
                print(data.decode())
            else:
                break


client = Client(SERVER_ADDRESS, SERVER_PORT)
client.run()
