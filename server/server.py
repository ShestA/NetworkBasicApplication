import logging
import socket
import threading
from typing import Union, List, Dict
from common_lib.utilities import retry
from network_lib.client import IRequestHandler
from network_lib.utilities import pack_data, send_data, get_packages
from network_lib.package import PackageType, isFin, isData, Package


class Client:
    __id: int
    __connection: socket
    __username: str

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

    @property
    def username(self):
        return self.__username

    @username.setter
    def username(self, username: str):
        self.__username = username


class ClientHandler:
    __active: bool
    __client: Client
    __listener_thread: threading.Thread
    __handlers: List[IRequestHandler]

    def __init__(self, client: Client):
        self.__active = True
        self.__client = client
        self.__handlers = []

    def connect(self, retries) -> str:
        if retry(self.__welcome_handshake__, retries) is False:
            raise ConnectionError()
        return self.__client.username

    def listen(self):
        self.__listener_thread = threading.Thread(target=self.__listen__)
        self.__listener_thread.start()

    def stop(self):
        self.__active = False

    def join(self):
        if self.__listener_thread is not None:
            self.__listener_thread.join()

    def disconnect(self):
        self.__good_bye__()

    def registerHandler(self, hdl: IRequestHandler):
        self.__handlers.append(hdl)

    def __listen__(self):
        try:
            while self.__active is True:
                try:
                    packages = get_packages(self.__client.connection, False)
                except ConnectionError:
                    continue
                if packages is None:
                    continue
                for hdl in self.__handlers:
                    hdl.handle(packages)
        except Exception as e:
            print(e, flush=True)

    def sendData(self, data: bytearray):
        if not self.__active:
            raise FileExistsError("Connection not established")
        packages = pack_data(PackageType.DATA, data)
        corruptions = send_data(self.__client.connection, packages, False)
        if len(corruptions) != 0:
            raise ConnectionError()

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
        self.__client.username = packages[0].data.decode("utf-8")
        packages = pack_data(PackageType.SYN_ACK, bytearray("Welcome, " + self.__client.username, "utf-8"))
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


class GoodByeHandler(IRequestHandler):
    __client: ClientHandler

    def __init__(self, client: ClientHandler):
        self.__client = client

    def handle(self, packages: List[Package]):
        if isFin(packages[0]):
            self.__client.stop()
            self.__client.disconnect()


class SendToClientMessageHandler(IRequestHandler):
    __client: ClientHandler
    __clients: Dict[str, ClientHandler]

    def __init__(self, client: ClientHandler, clients: Dict[str, ClientHandler]):
        self.__client = client
        self.__clients = clients

    def handle(self, packages: List[Package]):
        if isData(packages[0]) and packages[0].header.destination is not None:
            try:
                data = bytearray()
                for package in packages:
                    data = data + package.data
                self.__clients[packages[0].header.destination].sendData(data)
            except KeyError:
                ...


class Server:
    __active: bool
    __acc_id: int
    __master_socket: socket
    __clients_handlers: Dict[str, ClientHandler]

    def __init__(self, address: Union[tuple, str, bytes]):
        self.__active = True
        print("Starting server...", flush=True)
        self.__acc_id = 0
        self.__master_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__clients_handlers = {}
        try:
            self.__master_socket.bind(address)
        except OSError as e:
            print(e, flush=True)
            raise KeyboardInterrupt
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
                client_handler.registerHandler(GoodByeHandler(client_handler))
                client_handler.registerHandler(SendToClientMessageHandler(client_handler, self.__clients_handlers))
                username = client_handler.connect(3)
                client_handler.listen()
                self.__clients_handlers[username] = client_handler
            except BlockingIOError:
                ...
            except ConnectionError:
                ...
            except socket.timeout:
                ...
            dead_clients = []
            for key in self.__clients_handlers:
                connection = self.__clients_handlers[key]
                if not connection.isAlive():
                    dead_clients.append(key)
            for key in dead_clients:
                del self.__clients_handlers[key]

    def stop(self):
        print("Stopping server...", flush=True)
        self.__active = False
        for key in self.__clients_handlers:
            self.__clients_handlers[key].stop()
            self.__clients_handlers[key].join()
            self.__clients_handlers[key].disconnect()
        self.__clients_handlers.clear()

    def __del__(self):
        print("Close server...", flush=True)
        del self.__clients_handlers
        self.__master_socket.close()
        print("Closed", flush=True)
