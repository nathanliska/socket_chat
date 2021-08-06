import socket
#from threading import Thread
from concurrent.futures import ThreadPoolExecutor

SERVER_ADD = 'localhost'
SERVER_PORT = 8170
MESSAGE_SIZE = 2048
REQUESTS = 10


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
            print("Cannot connect to server: " + str(self.ip) + ":" + str(self.port) + " " + str(e))
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
                print("Connection closed! " + str(e))

            if data:
                print(data.decode())
            else:
                break


client = Client(SERVER_ADD, SERVER_PORT)
client.run()
