from dataclasses import dataclass
from common import OS
from installation.abstract import Installation

@dataclass(frozen=True)
class Dnf(Installation):
    PackageName: str
    Version: str | None = None

    @property
    def os(self) -> list[OS]:
        return [OS.fedora]

    @property
    def name(self) -> str:
        return self.PackageName
