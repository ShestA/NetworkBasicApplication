from typing import List

from .command import Command


class ShowHelp(Command):
    def __init__(self, args: List[str]):
        super().__init__(args)

    def execute(self):
        for cls in Command.__subclasses__():
            print(cls.help())

    @staticmethod
    def help() -> str:
        return "Show help:\n  help"
