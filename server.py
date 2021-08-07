import socket
from threading import Thread


#host_secondary = socket.gethostname()
SERVER_HOST_ADDRESS = 'localhost'
SERVER_PORT = 8170
REQUESTS = 100
MESSAGE_SIZE = 2048


def get_conn_addr_str(conn):
    return f"{format_address((conn.getpeername()[0], conn.getpeername()[1]))}"


def format_address(address):
    # address = (ip, port)
    return f"{address[0]}:{address[1]}"


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
        if conn in self.connections:
            self.connections.remove(conn)

    def send_msg(self, conn, msg):
        # try to send a message - close and remove connection if exception
        try:
            conn.send(msg.encode())
        except ConnectionError as e:
            print(f"Error sending to: {get_conn_addr_str(conn)} {e}")
            conn.close()
            self.remove_conn(conn)

    def send_to_all(self, msg):
        # send to all connections
        for conn in self.connections:
            self.send_msg(conn, msg)

    def broadcast(self, origin_conn, msg):
        # send to all but original connection
        for conn in self.connections:
            if conn != origin_conn:
                self.send_msg(conn, msg)

    def open_socket(self):
        try:
            # create and bind socket to address
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind(self.address)
        except socket.gaierror as e:
            print(f"Error creating/binding socket to: {format_address(self.address)} {e}")
            if self.server:
                self.server.close()
                exit(-1)

    def client_thread(self, ip, port, connection):
        # send the client a message confirming the connection
        #print("Incoming connection from: " + str(ip) + ":" + str(port))
        welcome_msg = f"You have joined the chat at: {get_conn_addr_str(connection)}"
        self.send_msg(connection, welcome_msg)

        while True:
            data = None

            try:
                # CLIENT MESSAGE HANDLER
                data = connection.recv(MESSAGE_SIZE)
            except ConnectionError as e:
                # CLIENT DISCONNECT HANDLER
                disconnect_msg = f"User <{format_address((ip, port))}> has left the chat!"
                #print("Connection to: " + get_conn_addr_str(connection) + " " + str(e))
                print(disconnect_msg)
                connection.close()
                self.remove_conn(connection)
                self.send_to_all(disconnect_msg)

            if data:
                # CLIENT DATA RECEIVED HANDLER
                data = data.decode()
                broadcast_msg = f"<{format_address((ip, port))}> {data}"
                print(broadcast_msg)
                self.send_to_all(broadcast_msg)
                #self.broadcast(connection, broadcast_msg)
            else:
                connection.close()
                self.remove_conn(connection)
                break

    def run(self):
        # open socket and listen for REQUESTS number of requests
        self.open_socket()
        self.server.listen(REQUESTS)
        print(f"Server listening at: {format_address(self.address)}")

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

                # add connection to list and broadcast new user
                new_user_msg = f"User <{format_address((ip, port))}> has joined the chat!"
                print(new_user_msg)
                self.connections.add(connection)
                self.broadcast(connection, new_user_msg)
                #print(self.connections)
            except ConnectionError as e:
                print(f"Socket error {e}")
                break
        self.server.close()


# instantiate a server and run it
server = Server(SERVER_HOST_ADDRESS, SERVER_PORT)
server.run()
