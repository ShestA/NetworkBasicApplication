import socket
import sys
import logging
from random import randrange

sys.path.append('../network_lib')

from utilities import get_data, pack_data, send_data


class Client:
    def __init__(self, username=""):
        logging.info("Starting client...")
        self.active = True
        self.master_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.dest_address = None

    def connect(self, address, retries=100):
        if self.dest_address is not None:
            raise FileExistsError("Connection already used")
        self.dest_address = address
        try:
            self.master_socket.connect(self.dest_address)
        except BlockingIOError:
            ...
        n = 0
        res = None
        while n < retries:
            n = n + 1
            res = self.__welcome_handshake__()
            if res is True:
                break
        if res is None:
            raise ConnectionError()

    def __welcome_handshake__(self):
        seq = randrange(int("0x00FFFFFF", 16)) + int("0xFF000000", 16)
        package = pack_data("SYN", seq)
        if not send_data(self.master_socket, package):
            logging.warning("Can't send message")
            return None
        package = get_data(self.master_socket)
        if package is None:
            return None
        if package["DATA"] != "SYN-ACK" and package["HEADER"]["ACK"] != seq + 1:
            return None
        ack = package["HEADER"]["SEQ"] + 1
        seq = package["HEADER"]["ACK"]
        data = pack_data("ACK", seq, ack)
        if not send_data(self.master_socket, data):
            logging.warning("Can't send message")
            return None
        return True

    def stop(self):
        logging.info("Stopping client...")
        self.active = False

    def __good_bye__(self):
        fin = randrange(int("0x00FFFFFF", 16)) + int("0xFF000000", 16)
        package = pack_data("FIN", 0, 0, fin)
        if not send_data(self.master_socket, package):
            # logging.warning("Can't send message")
            return False
        package = get_data(self.master_socket)
        if package is None:
            return False
        if not (package["DATA"] == "ACK" and package["HEADER"]["ACK"] == fin + 1):
            return False
        package = get_data(self.master_socket)
        if package is None:
            return False
        if not package["DATA"] == "FIN":
            return False
        package = pack_data("ACK", 0, package["HEADER"]["FIN"] + 1, fin)
        if not send_data(self.master_socket, package):
            # logging.warning("Can't send message")
            return False
        return True

    def __del__(self):
        self.active = False
        self.__good_bye__()
        self.master_socket.close()
