from dataclasses import dataclass
from common import OS

@dataclass(frozen=True)
class Dnf:
    PackageName: str
    Version: str | None = None

    @property
    def os(self) -> list[OS]: return [OS.fedora]

    @property
    def name(self) -> str: return self.PackageName
