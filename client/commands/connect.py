from socket import gaierror
from typing import List
from . import BadCommand
from . import ICommand
from network_lib.client import Client


class Connect(ICommand):
    __client: Client

    def __init__(self, client: Client):
        self.__client = client

    def execute(self, args: List[str]):
        try:
            address = args[0].split(":")[0]
            port = int(args[0].split(":")[1])
            self.__client.connect((address, port))
            self.__client.listen()
        except IndexError:
            raise BadCommand(f"Bad args '{' '.join(args)}'")
        except ValueError:
            raise BadCommand(f"Bad args '{' '.join(args)}'")
        except ConnectionRefusedError:
            raise BadCommand(f"{' '.join(args)} not available")
        except FileExistsError as e:
            raise BadCommand(e)
        except gaierror:
            raise BadCommand(f"{' '.join(args)} is a bad address")

    @staticmethod
    def help() -> str:
        return "Connect:\n  connect ip:port"
