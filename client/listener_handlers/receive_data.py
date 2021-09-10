from threading import Event
from typing import List

from network_lib.package import Package, isData
from network_lib.client import IRequestHandler, Client


class ReceiveDataHandler(IRequestHandler):
    __client: Client

    def __init__(self, client: Client):
        self.__client = client

    def handle(self, packages: List[Package]):
        if isData(packages[0]):
            data = bytearray()
            for package in packages:
                data = data + package.data
            print(data.decode("utf-8"))
