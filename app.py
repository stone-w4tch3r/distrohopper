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


@dataclass(frozen=True)
class App(_IUnit):
    Installation: Apt | Dnf | Snap | str
    Settings: list[ConfigEdit | TxtEdit] | None = None

    @property
    def name(self) -> str:
        # If Installation is str, return it; otherwise, use .name
        return self.Installation if isinstance(self.Installation, str) else self.Installation.name


def handle(apps: list[App]):
    apt_packages = [app.Installation for app in apps if isinstance(app.Installation, Apt)]
    dnf_packages = [app.Installation for app in apps if isinstance(app.Installation, Dnf)]
    snap_packages = [app.Installation for app in apps if isinstance(app.Installation, Snap)]
    str_packages = [app.Installation for app in apps if isinstance(app.Installation, str)]
    app_settings = [s for app in apps for s in app.Settings]
    config_edits = [s for s in app_settings if isinstance(s, ConfigEdit)]
    txt_edits = [s for s in app_settings if isinstance(s, TxtEdit)]

    distro: OS
    match host.get_fact(server_facts.LinuxDistribution)['name']:
        case 'Ubuntu':
            distro = OS.ubuntu
        case 'Debian':
            distro = OS.debian
        case 'Fedora':
            distro = OS.fedora
        case _:
            raise Exception('Unsupported OS')

    # todo: improve this check
    assert all([distro in package.os for package in apt_packages + dnf_packages + snap_packages]), 'OS mismatch'

    for ppa in [package.RepoOrPpa.PpaStr for package in apt_packages if isinstance(package.RepoOrPpa, AptPpa)]:
        # todo: apt.ppa is not idempotent, check if ppa is already added
        apt.ppa(src=ppa, _sudo=True)
        apt.update()
    for key, repo, pkg_name in [
        (package.RepoOrPpa.Key.url_str, package.RepoOrPpa.RepoSourceStr, package.name)
        for package in apt_packages
        if isinstance(package.RepoOrPpa, AptRepo)
    ]:
        apt.key(src=key, _sudo=True)
        apt.repo(src=repo, filename=pkg_name, _sudo=True)
        apt.update()  #todo: not dynamic!
    apt.packages(
        packages=[apt_package.PackageName for apt_package in apt_packages],
        cache_time=86400,
        update=True,
        _sudo=True
    )

    dnf.packages(
        packages=[dnf_package.PackageName for dnf_package in dnf_packages],
        _sudo=True
        # update=True,
    )

    snap.package(
        packages=[snap_package.PackageName for snap_package in snap_packages],
        _sudo=True
    )

    server.packages(
        packages=str_packages,
        _sudo=True
    )

    for c in config_edits:
        modify_file.modify_config_fluent(
            path=str(c.Path),
            modify_action=c.EditAction,
            config_type=modify_file.ConfigType[c.ConfigType.name.upper()]
        )
