from socket import gaierror
from typing import List
from . import BadCommand
from . import ICommand
from network_lib.client import Client


class Disconnect(ICommand):
    def __init__(self, client: Client):
        self.__client = client

    def execute(self, args: List[str]):
        try:
            self.__client.stop()
            self.__client.join()
            self.__client.disconnect()
        except FileExistsError as e:
            print(e, flush=True)

    @staticmethod
    def help() -> str:
        return "Disconnect:\n  disconnect"
