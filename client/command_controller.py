import threading
import sys
import select
from typing import Dict

from common_lib.exceptions import ExitException
from network_lib.client import Client
from commands import BadCommand, ICommand, ExitCommand, SendString, ShowHelp, Connect, Disconnect


def __input__():
    while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        line = sys.stdin.readline()
        if line and line != "\n":
            return line
        else:
            return ""
    return None


def __for_command__():
    sys.stdout.write(">> ")
    sys.stdout.flush()


class CommandController:
    __client: Client
    __listener_thread: threading.Thread
    __active: bool
    __commands: Dict[str, ICommand]

    def __init__(self, client: Client):
        self.__client = client
        self.__commands = {
            "exit": ExitCommand(self.__client),
            "help": ShowHelp,
            "send": SendString(self.__client),
            "connect": Connect(self.__client),
            "disconnect": Disconnect(self.__client),
        }

    def parse_command(self, command: str) -> [ICommand, str]:
        words = command.split()
        command = words[0]
        args = words[1:len(words)]
        try:
            return self.__commands[command], args
        except KeyError:
            raise BadCommand(f"Command {command} unrecognized")

    def run(self, exit_event: threading.Event):
        self.__active = True
        self.__listener_thread = threading.Thread(target=self.__listen__, args=[exit_event])
        self.__listener_thread.start()

    def stop(self):
        self.__active = False
        self.__listener_thread.join()
        self.__client.stop()

    def __listen__(self, exit_event: threading.Event):
        __for_command__()
        while self.__active:
            try:
                command = __input__()
                if command is None:
                    continue
                if len(command) == 0:
                    __for_command__()
                    continue
                try:
                    command, args = self.parse_command(command)
                    command.execute(args)
                    __for_command__()
                except ExitException:
                    print("Stopping", flush=True)
                    self.__active = False
                    exit_event.set()
                    break
                except BadCommand as e:
                    print(e.value, flush=True)
                    __for_command__()
            except KeyboardInterrupt:
                print("Stopping", flush=True)
                break
