from typing import List
from . import ICommand
from network_lib.client import Client


class SendString(ICommand):
    def __init__(self, client: Client):
        self.__client = client

    def execute(self, args: List[str]):
        try:
            username = args[0]
            args = args[1:len(args)]
            string = ' '.join(args)
            self.__client.send(username, bytearray(string, "utf-8"))
        except FileExistsError as e:
            print(e)

    @staticmethod
    def help() -> str:
        return "Send string:\n  send 'your_string'"
