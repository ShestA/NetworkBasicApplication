from functools import partial
from network_lib.client import Client
from commands import BadCommand, Command, ExitCommand, SendString, ShowHelp, Connect


class CommandController:

    def __init__(self, client: Client):
        self.__client = client
        self.__commands = {
            "exit": ExitCommand,
            "help": ShowHelp,
            "send": partial(SendString, self.__client),
            "connect": partial(Connect, self.__client)
        }

    def parse_command(self, command: str) -> Command:
        words = command.split()
        command = words[0]
        args = words[1:len(words)]
        try:
            return self.__commands[command](args)
        except KeyError:
            raise BadCommand(f"Command {command} unrecognized")

    def run(self):
        while True:
            command = input(">> ")
            if len(command) == 0:
                continue
            try:
                command = self.parse_command(command)
                command.execute()
            except BadCommand as e:
                print(e.value)
