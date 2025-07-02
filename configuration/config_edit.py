from typing import Callable
from pyinfra_lib import modify_file


class ConfigEdit:
    def __init__(self, Path: str, EditAction: Callable[[dict | list], dict | list], ConfigType: modify_file.ConfigType = modify_file.ConfigType.JSON):
        modify_file.modify_structured_config(
            path=Path,
            modify_action=EditAction,
            config_type=ConfigType,
        )
