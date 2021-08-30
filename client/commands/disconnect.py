from socket import gaierror
from typing import List
from . import BadCommand
from . import Command
from network_lib.client import Client


class Disconnect(Command):
    def __init__(self, client: Client, args: List[str]):
        super().__init__(args)
        self.__client = client

    def execute(self):
        try:
            self.__client.disconnect()
        except FileExistsError as e:
            print(e)

    @staticmethod
    def help() -> str:
        return "Disconnect:\n  disconnect"
