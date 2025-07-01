# Architecture & implementation notes

This document is aimed at **contributors/maintainers**.  It explains how the high-level API from `docs/api.md` is mapped to low-level `pyinfra` facts & operations, what is already implemented and what still needs work.

---

## 1. Control flow

```
apps_example.py (or user script)
        ↓ calls
app.handle([...])            # file app.py
        ↓ resolves current OS via server.LinuxDistribution fact
        ↓ sorts App objects into buckets (Apt/Dnf/Snap/str)
        ↓ generates idempotent operations
        ↓ executes through pyinfra runtime
```

pyinfra itself takes care of *connection*, *state* and *parallelism*.  Our responsibility is reduced to composing the correct sequence of **facts / operations**.

---

## 2. Mapping of API → pyinfra

| High-level feature | pyinfra primitives | Status |
|--------------------|--------------------|--------|
| `Apt` install & optional repo | `apt.repo`, `apt.key`, `apt.ppa`, `apt.packages` | ✅ implemented, but `apt.update()` is not optimised (runs too often) |
| `Dnf` install | `dnf.packages` | ✅ |
| `Snap` install | `snap.package` | ✅ |
| Generic string install | `server.packages` | ✅ (*will reuse pacman, zypper in future*) |
| Structured config patch | `files.get`, custom logic, `files.put` | ✅ (`lib/modify_file.py`) |
| Plain-text patch | same as above | ✅ |
| Remote Python snippet/file | `files.put`, raw shell command, `files.file` | ✅ (`lib/remote_python.py`) |
| OS detection | `server.LinuxDistribution` fact | ✅ |

Planned extensions:
* `Flatpak`, `Pacman`, `Zypper` install classes.
* `Service` abstraction – start/enable systemd units.
* A richer inventory approach (support user-provided OS mapping instead of auto-detection only).

---

## 3. Internal helpers overview

* **`units._IUnit`** – marker interface; currently only `App` implements it.
* **`common.URL`** – small validator.
* **`lib.modify_file`** – heavy lifting for file mutating operations.
    * Uses custom `DictWrapper`, `ListWrapper` to allow in-lambda edits while staying pure.
    * `ConfigType` supports JSON / INI / XML / plist; YAML/TOML could be added easily.
* **`lib.remote_python_*`** – locate interpreters on host, upload & execute code, clean up.

All helpers are written to be **idempotent** where it makes sense.  Non-idempotent call sites (`execute_string`, etc.) are flagged explicitly.

---

## 4. Needed pyinfra building blocks

Besides the stock pyinfra facts/operations we still miss:

1. `flatpak.install` – can be implemented via `command` for now but a first-class operation would be nicer.
2. `pacman.packages`, `zypper.packages` (contributions welcome).
3. Fact to detect `snapd` availability.
4. Maybe 
   ```python
   service.unit(name="ssh", enabled=True, started=True)
   ```
   – thin wrapper around `server.service` for declarative usage.

---

## 5. Directory / package layout (desired)

```
distrohopper/
├── app.py                 # public API entry
├── apps_example.py        # examples / e2e tests
├── common.py
├── units.py               # internal interfaces
│
├── lib/                   # implementation helpers (private)
│   ├── __init__.py
│   ├── modify_file.py
│   ├── remote_python.py
│   ├── remote_python_fact.py
│   ├── remote_python_util.py
│   └── tests.py
│
├── docs/
│   ├── api.md
│   └── arch.md
│
├── tests/                 # future pytest unit tests
│   └── ...
│
├── requirements.txt
├── README.md
└── LICENSE (to be added)
```

When new top-level abstractions appear (e.g. `Service`, `File`, `User`) they should live in their own modules to keep `app.py` focused on application installation.

---

_End of architecture notes_
