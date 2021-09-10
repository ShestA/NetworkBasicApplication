from typing import List


class ICommand:
    def execute(self, args: List[str]):
        ...

    @staticmethod
    def help() -> str:
        ...
