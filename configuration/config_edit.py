from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable

class StructuredConfigType(Enum):
    JSON = auto()
    YAML = auto()
    INI = auto()

@dataclass(frozen=True)
class ConfigEdit:
    Path: str
    EditAction: Callable[[dict | list], dict | list]
    ConfigType: StructuredConfigType = StructuredConfigType.JSON
