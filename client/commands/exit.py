from typing import List
from common_lib.exceptions import ExitException
from network_lib.client import Client

from . import ICommand


class ExitCommand(ICommand):
    __client: Client

    def __init__(self, client: Client):
        self.__client = client

    def execute(self, args: List[str]):
        try:
            self.__client.disconnect()
        except FileExistsError:
            ...
        raise ExitException

    @staticmethod
    def help() -> str:
        return "Exit:\n  exit"
