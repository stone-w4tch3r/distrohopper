from dataclasses import dataclass
from distutils.version import LooseVersion


class PythonVersion:
    major: int
    minor: int
    loose: LooseVersion
    full: str

    def __init__(self, version: str):
        if not isinstance(version, str):
            raise ValueError(f"Invalid Python version: {version}")

        bits = version.split(".")
        if len(bits) < 2:
            raise ValueError(f"Invalid Python version: {version}")
        if bits[0] not in ["2", "3"]:
            raise ValueError(f"Invalid Python version: {version}")
        if not bits[1].isdigit():
            raise ValueError(f"Invalid Python version: {version}")

        self.major = int(bits[0])
        self.minor = int(bits[1])
        self.loose = LooseVersion(version)
        self.full = version

    def __str__(self):
        return self.full


@dataclass(frozen=True)
class InterpreterInfo:
    version: PythonVersion
    path: str
