from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Callable

from pyinfra import host
from pyinfra.facts import server as server_facts
from pyinfra.operations import apt, dnf, snap, server, python

from common import OS
from lib import modify_file
from units import _IUnit
from abstractions.install import Apt, Dnf, Snap, AptRepo, AptPpa

from configuration.config_edit import ConfigEdit
from configuration.txt_edit import TxtEdit


class App(_IUnit):
    def __init__(self, Installation: dict[OS, Apt | Dnf | Snap | str], Settings: list[ConfigEdit | TxtEdit] | None = None):
        self.Installation_by_os = Installation
        self.Settings = Settings

        # Detect current OS
        distro_name = host.get_fact(server_facts.LinuxDistribution)['name']
        if distro_name == 'Ubuntu':
            self.os = OS.ubuntu
        elif distro_name == 'Debian':
            self.os = OS.debian
        elif distro_name == 'Fedora':
            self.os = OS.fedora
        else:
            raise Exception('Unsupported OS')

        # Select installation for this OS
        if self.os not in self.Installation_by_os:
            raise Exception(f'No installation specified for OS {self.os}')
        self.Installation = self.Installation_by_os[self.os]

        # Provision immediately
        self._provision()

    @property
    def name(self) -> str:
        return self.Installation if isinstance(self.Installation, str) else self.Installation.name

    def _provision(self):
        inst = self.Installation
        # Apt
        if isinstance(inst, Apt):
            if inst.RepoOrPpa:
                if isinstance(inst.RepoOrPpa, AptPpa):
                    apt.ppa(src=inst.RepoOrPpa.PpaStr, _sudo=True)
                    apt.update()
                elif isinstance(inst.RepoOrPpa, AptRepo):
                    apt.key(src=inst.RepoOrPpa.KeyUrl, _sudo=True)
                    apt.repo(src=inst.RepoOrPpa.RepoSourceStr, filename=inst.name, _sudo=True)
                    apt.update()
            apt.packages(
                packages=[inst.PackageName],
                cache_time=86400,
                update=True,
                _sudo=True
            )
        # Dnf
        elif isinstance(inst, Dnf):
            dnf.packages(
                packages=[inst.PackageName],
                _sudo=True
            )
        # Snap
        elif isinstance(inst, Snap):
            snap.package(
                packages=[inst.PackageName],
                _sudo=True
            )
        # String (generic package)
        elif isinstance(inst, str):
            server.packages(
                packages=[inst],
                _sudo=True
            )
        else:
            raise Exception(f'Unknown installation type: {type(inst)}')

        # Apply settings
        # TODO: what if we need to wait for the app to be installed before applying settings?
        if self.Settings:
            for s in self.Settings:
                if isinstance(s, ConfigEdit):
                    modify_file.modify_config_fluent(
                        path=str(s.Path),
                        modify_action=s.EditAction,
                        config_type=modify_file.ConfigType[s.ConfigType.name.upper()]
                    )
                elif isinstance(s, TxtEdit):
                    modify_file.modify_config_fluent(
                        path=str(s.Path),
                        modify_action=s.EditAction,
                        config_type=modify_file.ConfigType['TXT']
                    )
                else:
                    raise Exception(f'Unknown setting type: {type(s)}')


