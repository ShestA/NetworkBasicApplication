import logging
import socket
import threading
from typing import Union, List
from common_lib.utilities import delete_multiple_element, retry
from network_lib.utilities import pack_data, send_data, get_packages
from network_lib.package import PackageType, isFin, isData


class Client:
    __id: int
    __connection: socket

    def __init__(self, id: int, connection: socket):
        self.__id = id
        logging.info(f"New connection {self.__id}: connection={connection}")
        self.__connection = connection

    def __del__(self):
        logging.info(f"Closing connection {self.__id}: connection={self.__connection}")
        self.__connection.close()

    @property
    def connection(self):
        return self.__connection

    @property
    def id(self):
        return self.__id


class ClientHandler:
    __active: bool
    __client: Client
    __listener_thread: threading.Thread

    def __init__(self, client: Client):
        self.__active = True
        self.__client = client

    def connect(self, retries):
        if retry(self.__welcome_handshake__, retries) is False:
            raise ConnectionError()

    def listen(self):
        self.__listener_thread = threading.Thread(target=self.__listen__)
        self.__listener_thread.start()

    def stop(self):
        self.__active = False
        if self.__listener_thread is not None:
            self.__listener_thread.join()

    def disconnect(self):
        self.__good_bye__()

    def __listen__(self):
        try:
            while self.__active is True:
                try:
                    packages = get_packages(self.__client.connection, False)
                except ConnectionError:
                    continue
                if packages is None:
                    continue
                if isFin(packages[0]):
                    self.__good_bye__()
                    break
                for package in packages:
                    if isData(package):
                        print(package.data.decode("utf-8"))
        except Exception as e:
            print(e)

    def isAlive(self) -> bool:
        return self.__listener_thread.is_alive()

    def id(self) -> int:
        return self.__client.id

    def __welcome_handshake__(self) -> Union[bool, None]:
        packages = get_packages(self.__client.connection, False)
        if packages is None:
            return None
        if len(packages) != 1 or packages[0].header.type != PackageType.SYN:
            return None
        packages = pack_data(PackageType.SYN_ACK, bytearray("Welcome", "utf-8"))
        corruptions = send_data(self.__client.connection, packages, False)
        if len(corruptions) != 0:
            return None
        packages = get_packages(self.__client.connection, False)
        if packages is None:
            return None
        if len(packages) != 1 or packages[0].header.type != PackageType.ACK:
            return None
        return True

    def __good_bye__(self):
        self.__active = False
        packages = pack_data(PackageType.FIN, bytearray("Good bye", "utf-8"))
        send_data(self.__client.connection, packages, False)


class Server:
    __active: bool
    __acc_id: int
    __master_socket: socket
    __clients_handlers: List[ClientHandler]

    def __init__(self, address: Union[tuple, str, bytes]):
        self.__active = True
        print("Starting server...")
        self.__acc_id = 0
        self.__master_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__clients_handlers = []
        self.__master_socket.bind(address)
        self.__master_socket.setblocking(False)
        self.__master_socket.listen(10)
        self.__master_socket.settimeout(0.3)

    def run(self):
        while self.__active:
            try:
                connection, _ = self.__master_socket.accept()
                connection.setblocking(False)
                connection.settimeout(0.3)
                self.__acc_id = self.__acc_id + 1
                client_handler = ClientHandler(Client(self.__acc_id, connection))
                client_handler.connect(3)
                client_handler.listen()
                self.__clients_handlers.append(client_handler)
            except BlockingIOError:
                ...
            except ConnectionError:
                ...
            except socket.timeout:
                ...
            dead_clients = []
            for idx, connection in enumerate(self.__clients_handlers):
                if not connection.isAlive():
                    del connection
                    dead_clients.append(idx)
            delete_multiple_element(self.__clients_handlers, dead_clients)

    def stop(self):
        print("Stopping server...")
        self.__active = False
        for client_handler in self.__clients_handlers:
            client_handler.stop()
            client_handler.disconnect()
            del client_handler
        self.__clients_handlers.clear()

    def __del__(self):
        print("Close server...")
        del self.__clients_handlers
        self.__master_socket.close()
        print("Closed")
