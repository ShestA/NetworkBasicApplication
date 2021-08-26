import logging
import socket
import sys
import threading
from random import randrange
from typing import Union

sys.path.append('../network_lib')

from utilities import get_data, pack_data, send_data, delete_multiple_element


class Client:
    def __init__(self, id: int, connection: socket):
        self.id = id
        logging.info(f"New connection {self.id}: connection={connection}")
        self.connection = connection

    def __del__(self):
        logging.info(f"Closing connection {self.id}: connection={self.connection}")
        self.connection.close()


class ClientHandler:
    def __init__(self, client: Client, retries=100):
        self.active = True
        self.client = client
        self.handler_thread = None
        n = 0
        res = None
        while n < retries:
            n = n + 1
            res = self.__welcome_handshake__()
            if res is True:
                break
        if res is None:
            raise ConnectionError()
        self.handler_thread = threading.Thread(target=self.__handler__)
        self.handler_thread.start()

    def __del__(self):
        self.active = False
        if self.handler_thread is not None:
            self.handler_thread.join()
        del self.client

    def __welcome_handshake__(self):
        package = get_data(self.client.connection)
        if package is None:
            return None
        if package["DATA"] != "SYN":
            return None
        ack = package["HEADER"]["SEQ"] + 1
        seq = randrange(int("0xF0000000", 16)) + int("0x0FFFFFFF", 16)
        package = pack_data("SYN-ACK", seq, ack)
        if not send_data(self.client.connection, package):
            logging.warning("Can't send message")
            return None
        package = get_data(self.client.connection)
        if package is None:
            return None
        if package["DATA"] == "ACK" and package["HEADER"]["ACK"] == seq + 1:
            return True
        return None

    def __handler__(self):
        while self.active is True:
            package = get_data(self.client.connection)
            if package is None:
                continue
            if package["DATA"] == "FIN":
                self.__good_bye__(package)
                break

    def isAlive(self):
        return self.handler_thread.is_alive()

    def id(self):
        return self.client.id

    def __good_bye__(self, package):
        self.active = False
        ack = package["HEADER"]["FIN"] + 1
        seq = randrange(int("0x00FFFFFF", 16)) + int("0xFF000000", 16)
        package = pack_data("ACK", seq, ack)
        if not send_data(self.client.connection, package):
            # logging.warning("Can't send message")
            return False
        fin = randrange(int("0x00FFFFFF", 16)) + int("0xFF000000", 16)
        package = pack_data("FIN", seq, ack, fin)
        if not send_data(self.client.connection, package):
            # logging.warning("Can't send message")
            return False
        package = get_data(self.client.connection)
        if package is None:
            return False
        if package["DATA"] == "ACK":
            return True
        return False


class Server:
    def __init__(self, address: Union[tuple, str, bytes]):
        self.active = True
        print("Starting server...")
        self.acc_id = 0
        self.master_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections_handlers = []
        self.master_socket.bind(address)
        self.master_socket.setblocking(False)
        self.master_socket.listen(10)
        self.master_socket.settimeout(0.3)

    def run(self):
        while self.active:
            try:
                connection, _ = self.master_socket.accept()
                self.acc_id = self.acc_id + 1
                self.connections_handlers.append(ClientHandler(Client(self.acc_id, connection)))
            except BlockingIOError:
                ...
            except ConnectionError:
                ...
            except socket.timeout:
                ...
            dead_clients = []
            for idx, connection in enumerate(self.connections_handlers):
                if not connection.isAlive():
                    del connection
                    dead_clients.append(idx)
            delete_multiple_element(self.connections_handlers, dead_clients)

    def stop(self):
        self.active = False

    def __del__(self):
        print("Stopping server...")
        self.connections_handlers.clear()
        self.master_socket.close()
