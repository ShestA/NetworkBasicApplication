import socket
import logging
from typing import Union, List
from .utilities import pack_data, send_data, get_packages
from .package import PackageType, Package
import threading


class IRequestHandler:
    def handle(self, packages: List[Package]):
        ...


class Client:
    __username: str
    __active: bool
    __dest_address: Union[tuple, str, bytes, None]
    __handlers: List[IRequestHandler]
    __listener_thread: Union[threading.Thread, None]
    __master_socket: socket

    def __init__(self, username):
        logging.info("Starting client...")
        self.__username = username
        self.__active = False
        self.__dest_address = None
        self.__handlers = []
        self.__listener_thread = None

    def connect(self, address: Union[tuple, str, bytes], retries=100):
        if self.__dest_address is not None:
            raise FileExistsError("Connection already used")
        try:
            self.__master_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__master_socket.setblocking(False)
            self.__master_socket.settimeout(0.3)
            self.__master_socket.connect(address)
        except BlockingIOError:
            ...
        self.__active = True
        self.__dest_address = address
        res = None
        for _ in range(retries):
            res = self.__welcome_handshake__()
            if res is True:
                break
        if res is None:
            raise ConnectionError()

    def isConnected(self):
        return self.__dest_address is not None

    def registerHandler(self, hdl: IRequestHandler):
        self.__handlers.append(hdl)

    def listen(self):
        self.__listener_thread = threading.Thread(target=self.__listen__)
        self.__listener_thread.start()

    def stop(self):
        self.__active = False

    def join(self):
        if self.__listener_thread is not None:
            self.__listener_thread.join()

    def __listen__(self):
        while self.__active:
            try:
                packages = get_packages(self.__master_socket, False)
            except ConnectionError:
                continue
            except Exception as e:
                print(e)
                break
            if packages is None:
                continue
            for hdl in self.__handlers:
                hdl.handle(packages)

    def send(self, data: bytearray):
        if not self.__active:
            raise FileExistsError("Connection not established")
        packages = pack_data(PackageType.DATA, data)
        corruptions = send_data(self.__master_socket, packages, False)
        if len(corruptions) != 0:
            raise ConnectionError()

    def __welcome_handshake__(self) -> Union[bool, None]:
        packages = pack_data(PackageType.SYN, bytearray(self.__username, "utf-8"))
        corruptions = send_data(self.__master_socket, packages, False)
        if len(corruptions) != 0:
            return None
        packages = get_packages(self.__master_socket, False)
        if packages is None:
            return None
        if packages[0].header.type != PackageType.SYN_ACK:
            return None
        welcome_message = packages[0].data.decode("utf-8")
        print("Server:", welcome_message)
        packages = pack_data(PackageType.ACK, bytearray())
        corruptions = send_data(self.__master_socket, packages, False)
        if len(corruptions) != 0:
            return None
        return True

    def disconnect(self):
        if self.__dest_address is None:
            # raise FileExistsError("Connection not established")
            return
        self.__good_bye__()
        self.__master_socket.close()
        self.__dest_address = None
        print("Disconnected")

    def __good_bye__(self):
        try:
            packages = pack_data(PackageType.FIN, bytearray())
            corruptions = send_data(self.__master_socket, packages, False)
            if len(corruptions) != 0:
                return
            packages = get_packages(self.__master_socket, False)
            if packages is None:
                return
            good_by_message = packages[0].data.decode("utf-8")
            print("Server:", good_by_message)
            return
        except ConnectionRefusedError as e:
            print(e.strerror)
            return
        except BrokenPipeError as e:
            print(e.strerror)
            return
        except ConnectionError as e:
            print(e.strerror)
            return
