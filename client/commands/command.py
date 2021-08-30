from typing import List


class Command:
    def __init__(self, args: List[str]):
        ...

    def execute(self):
        ...

    @staticmethod
    def help() -> str:
        ...
