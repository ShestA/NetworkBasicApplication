import socket
import sys
import logging
from random import randrange
from typing import Union

sys.path.append('..')

from network_lib.utilities import get_data, pack_data, send_data, get_packages
from network_lib.package import PackageType


class Client:
    def __init__(self, username=""):
        logging.info("Starting client...")
        self.active = True
        self.master_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.dest_address = None

    def __del__(self):
        self.active = False
        self.__good_bye__()
        self.master_socket.close()

    def connect(self, address, retries=100):
        if self.dest_address is not None:
            raise FileExistsError("Connection already used")
        self.dest_address = address
        try:
            self.master_socket.connect(self.dest_address)
        except BlockingIOError:
            ...
        res = None
        for _ in range(retries):
            res = self.__welcome_handshake__()
            if res is True:
                break
        if res is None:
            raise ConnectionError()

    def __welcome_handshake__(self) -> Union[bool, None]:
        packages = pack_data(PackageType.SYN, bytearray())
        corruptions = send_data(self.master_socket, packages, False)
        if len(corruptions) != 0:
            return None
        packages = get_packages(self.master_socket, False)
        if packages is None:
            return None
        if packages[0].header.type != PackageType.SYN_ACK:
            return None
        welcome_message = packages[0].data.decode("utf-8")
        print("Server:", welcome_message)
        packages = pack_data(PackageType.ACK, bytearray())
        corruptions = send_data(self.master_socket, packages, False)
        if len(corruptions) != 0:
            return None
        return True

    def stop(self):
        logging.info("Stopping client...")
        self.active = False

    def __good_bye__(self):
        try:
            packages = pack_data(PackageType.FIN, bytearray())
            corruptions = send_data(self.master_socket, packages, False)
            if len(corruptions) != 0:
                return
            packages = get_packages(self.master_socket, False)
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
