from functools import partial
from network_lib.client import Client
from commands.bad_command import BadCommand
from commands.command import Command
from commands.exit import ExitCommand
from commands.send_string import SendString
from commands.show_help import ShowHelp


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
            except BadCommand as e:
                print(f"Command {e} unrecognized")
