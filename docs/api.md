# distrohopper User API Guide

This guide covers the essential public API for declaring and applying your environment with distrohopper.

---

## Quick Start

1. Install requirements and pyinfra:
   ```sh
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Write your environment file (see examples below).
3. Run:
   ```sh
   pyinfra inventory.py your_file.py --apply
   ```

---

## Main Concepts

### App

- The main unit. Represents an application to install, configure, and/or manage services for.
- Usage:
  ```python
  App(Installation, Settings=None, Services=None)
  ```
  - `Installation`: how to install (see below)
  - `Settings`: optional config file edits (list)
  - `Services`: optional systemd services to manage (list)

### Installation Types

Choose one per app:

| Type      | Platforms                      | Notes & Extras                             |
| --------- | ------------------------------ | ------------------------------------------ |
| `Apt`     | Ubuntu, Debian                 | Optionally add `AptRepo`, `AptPpa`         |
| `Dnf`     | Fedora                         | Optionally add `DnfRepo`, `Copr`           |
| `Snap`    | Ubuntu, Debian, Fedora (snapd) |                                            |
| `Flatpak` | Any with flatpak               | Optionally add `FlatpakRepo`, set `remote` |
| `Pacman`  | Arch, Manjaro                  |                                            |
| `Zypper`  | openSUSE, SLE                  |                                            |
| `str`     | any                            | Treated as native system package name      |

#### Example

```python
Apt("firefox")
Dnf("neovim", Copr("username/project"))
Flatpak("org.gimp.GIMP", remote="flathub", FlatpakRepo("flathub", "https://dl.flathub.org/repo/flathub.flatpakrepo"))
```

### Config and Service Helpers

- `ConfigModification(path, ModifyAction, ConfigType)` – patch JSON/INI/XML/plist.
- `PlainTextModification(ModifyAction)` – patch arbitrary text files.
- `Service(name, enabled=True, started=True)` – ensure a systemd service is enabled/started.

```python
App(Installation, Settings=None, Services=None)
```

- `Installation` – one of the install methods above.
- `Settings` – list of modifications that will be executed **in order** after the package is present.
- `Services` – _(optional)_ list of `Service` abstractions to enable/start after install (see below).

#### Service abstraction

```python
class Service:
    def __init__(self, name: str, enabled: bool = True, started: bool = True, restarted: bool = False, user: str = None):
        ...
```

- Maps to pyinfra: `server.service` (or future `service.unit`).
- Idempotent: will only make changes if state differs.
- Example usage:

```python
App(
    Installation=Apt("openssh-server"),
    Services=[Service("ssh", enabled=True, started=True)]
)
```

---

## 2. Using the API

### 2.1 Minimal example

```python
from app import App, Apt
from common import OS

apps = [
    App(Apt("neofetch")),
]

app.handle(apps)  # generates pyinfra operations based on the current host
```

Run with:

```
pyinfra inventory.py your_file.py --apply
```

### 2.2 Multi-distro selection

```python
from app import App, Apt, Dnf
from common import OS

current_os = OS.ubuntu  # can be detected automatically at runtime

apps = [
    App(({OS.ubuntu: Apt("firefox"), OS.fedora: Dnf("firefox")} )[current_os])
]
```

### 2.3 Flatpak and Service example

```python
from app import App, Flatpak, Service

apps = [
    App(
        Installation=Flatpak("org.gimp.GIMP", remote="flathub"),
        Services=[Service("gimp", enabled=True, started=True)]
    )
]
```

### 2.4 Pacman/Zypper example

```python
from app import App, Pacman, Zypper

apps = [
    App(Pacman("neovim")),
    App(Zypper("htop")),
]
```

### 2.5 Adding a third-party repo and editing JSON config

```python
from app import App, Apt, AptRepo, ConfigModification

apps = [
    App(
        Installation=Apt(
            "codium",
            AptRepo(
                KeyUrl="https://gitlab.com/paulcarroty/vscodium-deb-rpm-repo/raw/master/pub.gpg",
                RepoSourceStr="deb https://download.vscodium.com/debs vscodium main",
            ),
        ),
        Settings=[
            ConfigModification(
                Path="/usr/share/codium/resources/app/product.json",
                ModifyAction=lambda c: c["quality"].set("stable"),
            ),
        ],
    ),
]
```

### 2.6 Plain-text patch

```python
from app import App, Snap, PlainTextModification

apps = [
    App(
        Snap("micro-editor"),
        Settings=[
            PlainTextModification(lambda txt: txt.replace("tabsize=2", "tabsize=4")),
        ],
    )
]
```

---

## 3. Advanced helpers & extension

### 3.1 Editing dicts/lists in lambdas

To edit a dict or list in a lambda, use plain Python operations. For example:

```python
# For dicts:
ConfigModification(
    Path="/some/file.json",
    ModifyAction=lambda cfg: (cfg.update({"foo": 42}), cfg)[1]
)

# For lists:
ConfigModification(
    Path="/some/file.json",
    ModifyAction=lambda lst: (lst.append("bar"), lst)[1]
)
```

Or, for more complex edits, define a helper function:

```python
def add_car(cfg):
    cfg["cars"]["car2"] = {"name": "Audi", "year": 2022}
    return cfg

ConfigModification(
    Path="/some/file.json",
    ModifyAction=add_car
)
```

### 3.2 Executing Python on the host

```python
from lib import remote_python as rp

rp.execute_string("print('hello')")

rp.execute_function(
    func=my_local_fn,
    func_args=["arg1"],
    func_kwargs={"kw": "42"},
    minimum_python_version="3.8",
)
```

_Non-idempotent_ – will always run.

### 3.3 Extending with new install/service types

- To add a new package manager, implement a new install class (see `Flatpak`, `Pacman`, etc above) and map to a pyinfra operation or custom shell command.
- To add a new service abstraction, implement a `Service` subclass and map to `server.service` or a custom pyinfra operation.
- To add new config file types, extend `lib.modify_file` with a new parser/patcher.
- To add new host facts, implement a pyinfra Fact (see pyinfra docs for `FactBase`).

### 3.4 Error handling, idempotency, dry-run

- All install/config/service abstractions are idempotent and safe to re-run.
- Non-idempotent actions (remote Python, etc) are explicitly flagged.
- Unsupported OS/manager combinations raise a clear error at runtime.
- All operations respect pyinfra’s dry-run mode (`--dry-run`).

---

## 4. Public surface summary

```
common.OS, common.URL

installation.Apt, installation.Dnf, installation.Snap, installation.AptRepo, installation.AptPpa
configuration.ConfigEdit, configuration.TxtEdit, configuration.StructuredConfigType
app.App, app.handle

pyinfra_lib.modify_file.{modify_config_fluent, modify_structured_config, modify_plaintext_file}
pyinfra_lib.remote_python.{execute_string, execute_file, execute_function}
```

Everything else is private.

---

## 5. Changelog & roadmap

- [x] Multi-OS package install (Apt, Dnf, Snap, generic)
- [x] Structured/plain config patching
- [x] Remote Python execution
- [ ] Flatpak, Pacman, Zypper install
- [ ] Service abstraction
- [ ] Custom facts for snapd/flatpak detection
- [ ] YAML/TOML config support
- [ ] User/file abstractions
