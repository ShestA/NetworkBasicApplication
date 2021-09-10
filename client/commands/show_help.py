from typing import List
from .command import ICommand


class ShowHelp(ICommand):

    def execute(self):
        for cls in ICommand.__subclasses__():
            print(cls.help(), flush=True)

    @staticmethod
    def help() -> str:
        return "Show help:\n  help"
