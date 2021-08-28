import sys
from socket import socket
from functools import partial
from typing import List

from client import Client

sys.path.append('..')

from network_lib.package import PackageType
from network_lib.utilities import pack_data, send_data, ExitException


class BadCommand(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Command:
    def __init__(self, args: List[str]):
        ...

    def execute(self):
        ...

    @staticmethod
    def help() -> str:
        ...


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


class ExitCommand(Command):
    def __init__(self, args: List[str]):
        super().__init__(args)

    def execute(self):
        raise ExitException

    @staticmethod
    def help() -> str:
        return "Exit:\n  exit"


class ShowHelp(Command):
    def __init__(self, args: List[str]):
        super().__init__(args)

    def execute(self):
        for cls in Command.__subclasses__():
            print(cls.help())

    @staticmethod
    def help() -> str:
        return "Show help:\n  help"


class CommandController:

    def __init__(self, client: Client):
        self.__client = client
        self.__commands = {
            "exit": ExitCommand,
            "help": ShowHelp,
            "send": partial(SendString, self.__client)
        }

    def parse_command(self, command: str) -> Command:
        if len(command) == 0:
            raise BadCommand(command)
        words = command.split()
        command = words[0]
        args = words[1:len(words)]
        try:
            return self.__commands[command](args)
        except KeyError:
            raise BadCommand(command)

    def run(self):
        while True:
            command = input(">> ")
            if len(command) == 0:
                continue
            try:
                command = self.parse_command(command)
                command.execute()
            except BadCommand:
                print(f"Command '{command}' unrecognized")
