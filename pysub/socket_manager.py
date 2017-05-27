"""Module to handle socket connections and messaging"""
import socket

class SocketManager():
    """Handles a socket connection"""
    socket = None

    def __init__(self, server_address, server_port, verbose):
        self.server_address = server_address
        self.server_port = server_port
        self.verbose = verbose

    def is_connected(self):
        """Returns true if currently connected to a socket"""
        return self.socket is not None

    def connect(self):
        """Connects to the socket"""
        if self.is_connected():
            raise IOError("Already Connected")
        if not self.server_address.strip():
            raise ValueError("Empty server address")
        if self.server_port < 1:
            raise ValueError("Invalid server port: {0}".format(self.server_port))

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.server_address, self.server_port))

    def disconnect(self):
        """Disconnects and closes the socket"""
        if self.socket is not None:
            self.socket.close()
            self.socket = None

    def send_message(self, message):
        """Sends a message via socket"""
        message = str(message)
        if not message.strip():
            raise ValueError("Cannot send null or empty message")
        if "\n" in message:
            raise ValueError("Cannot send multiline messages")

        message += "\n"
        byte_message = message.encode('utf-8')
        if self.is_connected():
            if self.verbose:
                print("SEND: {0}".format(message))
            total_sent = 0
            while total_sent < len(byte_message):
                sent = self.socket.send(byte_message[total_sent:])
                if sent == 0:
                    raise RuntimeError("Socket connection broken")
                total_sent = total_sent + sent
        else:
            raise IOError("Not Connected")


    def receive_message(self):
        """Receives a message via socket"""
        if self.is_connected():
            delimiter_received = False
            message_list = list()
            while not delimiter_received:
                message_chunk = self.socket.recv(1).decode('utf-8')
                if not message_chunk:
                    break
                message_list.append(message_chunk)
                if "\n" in message_chunk:
                    delimiter_received = True
            message = ''.join(message_list).strip()
            if self.verbose:
                print("RECV: {0}".format(message))
            if "\n" in message:
                raise ValueError("You accidentally got two messages")
            return message
        else:
            raise IOError("Not Connected")
