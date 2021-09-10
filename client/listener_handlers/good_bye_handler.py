from threading import Event
from typing import List

from network_lib.package import Package, isFin
from network_lib.client import IRequestHandler, Client


class GoodByeHandler(IRequestHandler):
    __client: Client

    def __init__(self, client: Client):
        self.__client = client

    def handle(self, packages: List[Package]):
        if isFin(packages[0]):
            self.__client.stop()
            self.__client.disconnect()
