from socket import gaierror
from typing import List
from . import BadCommand
from . import Command
from network_lib.client import Client


class Connect(Command):
    def __init__(self, client: Client, args: List[str]):
        super().__init__(args)
        try:
            self.__address = args[0].split(":")[0]
            self.__port = int(args[0].split(":")[1])
        except IndexError:
            raise BadCommand(f"Bad args '{' '.join(args)}'")
        except ValueError:
            raise BadCommand(f"Bad args '{' '.join(args)}'")
        self.__client = client

    def execute(self):
        try:
            self.__client.connect((self.__address, self.__port))
        except ConnectionRefusedError:
            raise BadCommand(f"{self.__address}:{self.__port} not available")
        except FileExistsError as e:
            raise BadCommand(e)
        except gaierror:
            raise BadCommand(f"{self.__address}:{self.__port} is a bad address")

    @staticmethod
    def help() -> str:
        return "Connect:\n  connect ip:port"
