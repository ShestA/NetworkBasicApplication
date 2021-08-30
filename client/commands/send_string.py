from typing import List
from .command import Command
from network_lib.client import Client


class SendString(Command):
    def __init__(self, client: Client, args: List[str]):
        super().__init__(args)
        self.__string = ' '.join(args)
        self.__client = client

    def execute(self):
        self.__client.send(bytearray(self.__string, "utf-8"))

    @staticmethod
    def help() -> str:
        return "Send string:\n  send 'your_string'"
