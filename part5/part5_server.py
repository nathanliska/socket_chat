import socket
from threading import Thread

from datetime import datetime

#host_secondary = socket.gethostname()
SERVER_HOST_ADDRESS = 'localhost'
SERVER_PORT = 8170
REQUESTS = 100
MESSAGE_SIZE = 2048


def format_address(address):
    # address = (ip, port)
    return f"{address[0]}:{address[1]}"


def get_current_time():
    return datetime.now().strftime("%H:%M:%S")


class Server:
    """The Server class contains a server socket connection and can receive from and sent to a set of client connections"""
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.address = (self.ip, self.port)
        self.server = None
        self.connections = set()

    def remove_conn(self, conn):
        # close and remove connection
        conn.close()
        if conn in self.connections:
            self.connections.remove(conn)

    def send_msg(self, conn, msg):
        # try to send a message
        # if connection no longer exists or is interrupted sending
        # close and remove connection
        if conn.fileno() != -1:
            try:
                conn.sendall(msg.encode())
            except ConnectionError as e:
                print(f"[{get_current_time()}] [CONSOLE] Error sending data {e}")
                self.remove_conn(conn)
        else:
            self.remove_conn(conn)

    def receive_msg(self, conn):
        # attempt to receive data from a connection
        # pauses until data received or disconnect
        data = None
        try:
            # RECEIVE data
            data = conn.recv(MESSAGE_SIZE)
        except ConnectionError as e:
            self.remove_conn(conn)
        return data

    def send_to_all(self, msg):
        # send to all connections
        # create copy of connections set for iteration
        connections_copy = self.connections.copy()
        for conn in connections_copy:
            self.send_msg(conn, msg)

    def broadcast(self, origin_conn, msg):
        # send to all but original connection
        # create copy of connections set for iteration
        connections_copy = self.connections.copy()
        for conn in connections_copy:
            if conn != origin_conn:
                self.send_msg(conn, msg)

    def open_socket(self):
        # create and bind socket to address
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind(self.address)
        except (socket.gaierror, OSError) as e:
            print(f"[{get_current_time()}] [CONSOLE] Error creating/binding socket to: {format_address(self.address)} {e}")
            if self.server:
                self.server.close()
                exit(-1)

    def client_thread(self, ip, port, connection):
        # add connection to list and print connection info
        self.connections.add(connection)
        print(f"[{get_current_time()}] [CONSOLE] Incoming connection from: {format_address((ip, port))}")

        # send confirmation to connection and broadcasts new user
        self.send_msg(connection, f"[{get_current_time()}] You have joined the chat at <{format_address((ip, port))}!>")
        self.broadcast(connection, f"[{get_current_time()}] User <{format_address((ip, port))}> has joined the chat!")

        # loop to handle receiving and sending data
        while True:
            data = self.receive_msg(connection)

            if data:
                # CLIENT DATA RECEIVED HANDLER
                data = data.decode()
                broadcast_msg = f"[{get_current_time()}] <{format_address((ip, port))}>: {data}"
                print(broadcast_msg)
                self.broadcast(connection, broadcast_msg)
                # self.send_to_all(broadcast_msg)
            else:
                self.remove_conn(connection)
                disconnect_msg = f"[{get_current_time()}] User <{format_address((ip, port))}> has left the chat!"
                print(f"[{get_current_time()}] [CONSOLE] Disconnect from: {format_address((ip, port))}")
                self.send_to_all(disconnect_msg)
                break

    def run(self):
        # open socket and listen for REQUESTS number of requests
        self.open_socket()
        self.server.listen(REQUESTS)
        print(f"[{get_current_time()}] Server listening at: {format_address(self.address)}")

        # while loop to accept new connections
        while True:
            try:
                # CLIENT CONNECTION HANDLER
                # accepts a new client connection
                connection, (ip, port) = self.server.accept()

                # handle connection with thread
                conn_thread = Thread(target=self.client_thread, args=(ip, port, connection))
                conn_thread.daemon = True
                conn_thread.start()
            except ConnectionError as e:
                print(f"Socket error {e}")
                break
        self.server.close()


# instantiate a server and run it
server = Server(SERVER_HOST_ADDRESS, SERVER_PORT)
server.run()
