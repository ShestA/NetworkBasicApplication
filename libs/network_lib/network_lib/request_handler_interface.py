from typing import List

from .package import Package


class IRequestHandler:
    def handle(self, packages: List[Package]):
        ...
