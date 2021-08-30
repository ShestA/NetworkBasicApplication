from typing import List
from common_lib.exceptions import ExitException
from . import Command


class ExitCommand(Command):
    def __init__(self, args: List[str]):
        super().__init__(args)

    def execute(self):
        raise ExitException

    @staticmethod
    def help() -> str:
        return "Exit:\n  exit"
