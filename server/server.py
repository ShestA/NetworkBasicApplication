import logging
import socket
import sys
import threading
from typing import Union

sys.path.append('..')

from network_lib.utilities import get_data, pack_data, send_data, get_packages, delete_multiple_element
from network_lib.package import PackageType


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

    def __welcome_handshake__(self) -> Union[bool, None]:
        packages = get_packages(self.client.connection, False)
        if packages is None:
            return None
        if len(packages) != 1 or packages[0].header.type != PackageType.SYN:
            return None
        packages = pack_data(PackageType.SYN_ACK, bytearray("Welcome", "utf-8"))
        corruptions = send_data(self.client.connection, packages, False)
        if len(corruptions) != 0:
            return None
        packages = get_packages(self.client.connection, False)
        if packages is None:
            return None
        if len(packages) != 1 or packages[0].header.type != PackageType.ACK:
            return None
        return True

    @staticmethod
    def isFin(package) -> bool:
        return package.header.type == PackageType.FIN

    def __handler__(self):
        try:
            while self.active is True:
                packages = get_packages(self.client.connection, False)
                if packages is None:
                    continue
                if self.isFin(packages[0]):
                    self.__good_bye__()
                    break
        except Exception:
            ...

    def isAlive(self) -> bool:
        return self.handler_thread.is_alive()

    def id(self) -> int:
        return self.client.id

    def __good_bye__(self):
        self.active = False
        packages = pack_data(PackageType.FIN, bytearray("Good bye", "utf-8"))
        send_data(self.client.connection, packages, False)


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
        print("Stopping server...")
        self.active = False
        self.connections_handlers.clear()

    def __del__(self):
        print("Close server...")
        del self.connections_handlers
        self.master_socket.close()
        print("Closed")
