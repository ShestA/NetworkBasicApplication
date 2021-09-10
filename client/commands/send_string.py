from typing import List
from . import ICommand
from network_lib.client import Client


class SendString(ICommand):
    def __init__(self, client: Client):
        self.__client = client

    def execute(self, args: List[str]):
        try:
            string = ' '.join(args)
            self.__client.send(bytearray(string, "utf-8"))
        except FileExistsError as e:
            print(e)

    @staticmethod
    def help() -> str:
        return "Send string:\n  send 'your_string'"
