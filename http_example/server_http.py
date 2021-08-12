import socket
from threading import Thread

from datetime import datetime

#host_secondary = socket.gethostname()
SERVER_HOST_ADDRESS = 'localhost'
SERVER_PORT = 8170
REQUESTS = 100
MESSAGE_SIZE = 2048

IMAGE_LOC = "icon.png"


def get_conn_addr_str(conn):
    return f"{format_address((conn.getpeername()[0], conn.getpeername()[1]))}"


def format_address(address):
    # address = (ip, port)
    return f"{address[0]}:{address[1]}"


def get_current_time():
    return datetime.now().strftime("%H:%M:%S")


# this class contains a server socket and can receive from and sent to client connections
class Server:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.address = (self.ip, self.port)
        self.server = None
        self.connections = set()

    def remove_conn(self, conn):
        # remove connection
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
        # blocking until data received or disconnect
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

        # receive and decode request headers from connection
        request_header = None
        data = self.receive_msg(connection)
        if data is not None and data != b'':
            request_header = data.decode()
        else:
            print(f"[{get_current_time()}] [CONSOLE] No request headers received, closing...")
            self.remove_conn(connection)
            exit(-1)

        # if the icon is being requested
        if "favicon.ico" in request_header:
            print(f"[{get_current_time()}] [CONSOLE] Sending icon response and disconnecting: {format_address((ip, port))}")
            with open(IMAGE_LOC, "rb") as image:
                f = image.read()
                b = bytearray(f)

            response_header = f"HTTP/1.1 OK\r\nServer: Python 3.9 Server\r\nContent-Type: image/png; encoding=utf-8\r\nContent-Length: {len(b)}\r\nConnection: Close\r\n\r\n"
            self.send_msg(connection, response_header)
            connection.sendall(b)
        # if anything else is requested
        else:
            # create a response body and response header
            response_body = f"<html><head><title>Socket Test!</title></head><body><h1>Hello Connection <{format_address((ip, port))}>!</h1><p>{request_header}</p></body></html>"
            response_header = f"HTTP/1.1 OK\r\nServer: Python 3.9 Server\r\nContent-Type: text/html; encoding=utf-8\r\nContent-Length: {len(response_body)}\r\nConnection: Close\r\n\r\n"

            print(f"[{get_current_time()}] [CONSOLE] Sending html response and disconnecting: {format_address((ip, port))}")
            # send the response header and body and close connection
            self.send_msg(connection, response_header)
            self.send_msg(connection, response_body)
            self.remove_conn(connection)

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
