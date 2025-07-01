# API reference

This document describes the **public API** exposed by `distrohopper`.  Everything else in the code-base is considered *private* and may change without notice.

---

## 1. Data model

### 1.1 OS enum
```python
from common import OS
```
Represents the target distribution.  Currently supported:
* `OS.ubuntu`
* `OS.debian`
* `OS.fedora`

### 1.2 Installation methods

Choose **one** of the following dataclasses per app:

| Class | Distros | Parameters |
|-------|---------|------------|
| `Apt`  | Ubuntu, Debian | `PackageName`, `Version`, optional `RepoOrPpa` *(see below)* |
| `Dnf`  | Fedora | `PackageName`, `Version` |
| `Snap` | Ubuntu, Debian, Fedora (if snapd installed) | `PackageName`, `Version` |
| `str`  | any | fallback – the string is treated as a *system package* name and installed with the native manager (`apt`/`dnf`/`pacman` once implemented) |

`AptRepo` and `AptPpa` helpers describe additional repositories to enable before installing a package.

### 1.3 Configuration changes

After an app is installed you can **patch its config files**:

* `ConfigModification(path, ModifyAction, ConfigType)` – for JSON, INI, XML, plist.  `ModifyAction` receives the config as a dict or list. You can use a lambda or helper function to mutate and return the config. For example: `lambda cfg: cfg.update({"foo": 42}) or cfg`.
* `PlainTextModification(ModifyAction)` – for arbitrary text files; receives and must return a `str`.

### 1.4 The `App` unit
```python
App(Installation, Settings=None)
```
`Installation` – one of the install methods above.
`Settings` – list of modifications that will be executed **in order** after the package is present.

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

### 2.3 Adding a third-party repo and editing JSON config
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

### 2.4 Plain-text patch
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

## 3. Advanced helpers

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
*Non-idempotent* – will always run.

---

## 4. Public surface summary

```
common.OS, common.URL

app.Apt, app.Dnf, app.Snap, app.AptRepo, app.AptPpa
app.StructuredConfigType, app.ConfigModification, app.PlainTextModification
app.App, app.handle

lib.modify_file.{modify_config_fluent, modify_structured_config, modify_plaintext_file}
lib.remote_python.{execute_string, execute_file, execute_function}
```

Everything else is private.

---

_End of document_
