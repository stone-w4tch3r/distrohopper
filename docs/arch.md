# Architecture & implementation notes

This document is aimed at **contributors/maintainers**. It explains how the high-level API from `docs/api.md` is mapped to low-level `pyinfra` facts & operations, what is already implemented and what still needs work.

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

pyinfra itself takes care of _connection_, _state_ and _parallelism_. Our responsibility is reduced to composing the correct sequence of **facts / operations**.

---

## 2. Mapping of API → pyinfra

| High-level feature      | pyinfra primitives                                       | Status/Notes                                       |
| ----------------------- | -------------------------------------------------------- | -------------------------------------------------- |
| `Apt` install & repo    | `apt.repo`, `apt.key`, `apt.ppa`, `apt.packages`         | ✅ implemented, `apt.update()` not fully optimized |
| `Dnf` install           | `dnf.packages`                                           | ✅ implemented                                     |
| `Snap` install          | `snap.package`                                           | ✅ implemented                                     |
| `Flatpak` install       | `command` (custom wrapper), planned: `flatpak.install`   | ⚠️ WIP: wrapper uses shell, first-class op planned |
| `Pacman` install        | `pacman.packages` (planned), fallback: `server.packages` | ⚠️ Not yet implemented, design ready               |
| `Zypper` install        | `zypper.packages` (planned), fallback: `server.packages` | ⚠️ Not yet implemented                             |
| Generic string install  | `server.packages` (auto-selects best available)          | ✅ implemented                                     |
| Structured config patch | `files.get`, custom logic, `files.put`                   | ✅ (`lib/modify_file.py`)                          |
| Plain-text patch        | same as above                                            | ✅                                                 |
| Remote Python snippet   | `files.put`, shell, `files.file`                         | ✅ (`lib/remote_python.py`)                        |
| OS detection            | `server.LinuxDistribution` fact                          | ✅                                                 |
| Service abstraction     | `server.service`, planned: `service.unit` wrapper        | ⚠️ WIP: planned for declarative enable/start/stop  |
| Detect snapd/flatpak    | Custom fact (planned)                                    | ⚠️ Needed for robust Snap/Flatpak support          |

**Planned extensions:**

- `Flatpak`, `Pacman`, `Zypper` install classes (see above).
- Richer inventory: allow user-provided OS mapping, not just auto-detect.
- More config file types: YAML, TOML, etc.
- Custom facts for snapd/flatpak detection.

---

### pyinfra Execution Model & Facts

- **pyinfra** handles SSH/local/Docker connections, parallelism, and state tracking.
- **Facts**: Used for OS detection, capability checks, and custom logic (e.g., `server.LinuxDistribution`, custom `snapd_available`, etc).
- **Operations**: Each install/config/command maps to a pyinfra operation (idempotent by default).
- **Idempotency**: All operations and helpers are written to be idempotent where possible; non-idempotent actions (e.g., remote Python execution) are flagged.
- **Dry-run**: pyinfra supports dry-run (`--dry-run`), which is respected by all generated operations.
- **Error handling**: All failures are surfaced via pyinfra’s reporting; custom error messages are used for unsupported OS/operation combos.

---

### Extension Points

- **Adding a new package manager**: Implement a new install class (e.g., `Flatpak`, `Pacman`, `Zypper`) and map to pyinfra operation or custom shell as needed. Register in the main bucketing logic in `app.handle`.
- **Adding config file types**: Extend `lib.modify_file` to support new formats (YAML, TOML, etc) using the same idempotent patching logic.
- **Adding new facts**: Write a custom pyinfra fact (see pyinfra’s `FactBase`), use for detection (e.g., `snapd`, `flatpak` availability).

---


### Example: Flatpak Install

```python
# Planned API
Flatpak(
    package="org.gimp.GIMP",
    remote="flathub",  # optional
)
# Maps to: pyinfra operation (custom or future flatpak.install)
```

### Example: Pacman Install

```python
# Planned API
Pacman(
    package="neovim",
    version=None,
)
# Maps to: pyinfra operation pacman.packages (planned)
```

---

### Idempotency & Error Handling

- All install/config abstractions must be idempotent (safe to re-run).
- Non-idempotent actions (e.g., remote Python) must be explicitly documented.
- All unsupported OS or missing feature errors are surfaced early, with actionable error messages.
- Dry-run is supported for all operations via pyinfra.

---

### Roadmap

- [x] Multi-OS package install (Apt, Dnf, Snap, generic)
- [x] Structured/plain config patching
- [x] Remote Python execution
- [ ] Flatpak, Pacman, Zypper install
- [ ] Service abstraction
- [ ] Custom facts for snapd/flatpak detection
- [ ] YAML/TOML config support

---

---

## 3. Internal helpers overview

- **`units._IUnit`** – marker interface; currently only `App` implements it.
- **`common.URL`** – small validator.
- **`lib.modify_file`** – heavy lifting for file mutating operations.
  - `ConfigType` supports JSON / INI / XML / plist; YAML/TOML could be added easily.
- **`lib.remote_python_*`** – locate interpreters on host, upload & execute code, clean up.

All helpers are written to be **idempotent** where it makes sense. Non-idempotent call sites (`execute_string`, etc.) are flagged explicitly.

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

## 5. Directory / package layout (current)

```
distrohopper/
├── app.py                 # public API entry & orchestration
├── apps_example.py        # examples / e2e tests
├── common.py
├── units.py               # internal interfaces
│
├── pyinfra_lib/           # pyinfra operations/facts/helpers
│   ├── __init__.py
│   ├── modify_file.py
│   ├── remote_python.py
│   ├── remote_python_fact.py
│   ├── remote_python_util.py
│
├── installation/          # install method abstractions (Apt, Dnf, Snap, ...)
│   ├── __init__.py
│   ├── apt.py
│   ├── dnf.py
│   └── snap.py
│
├── configuration/         # config edit abstractions (ConfigEdit, TxtEdit, ...)
│   ├── config_edit.py
│   └── txt_edit.py
│
├── docs/
│   ├── api.md
│   └── arch.md
│
├── tests/
│   └── .gitkeep
│
├── requirements.txt
├── README.md
└── LICENSE (to be added)
```

- Install logic is modularized under `installation/` (e.g., `Apt`, `Dnf`, `Snap`).
- Configuration edit logic is modularized under `configuration/` (e.g., `ConfigEdit`, `TxtEdit`).
- File, service, and user management use pyinfra built-in operations directly; no custom abstractions are planned for these.
- `app.py` focuses on orchestration and mapping high-level API to pyinfra operations.

---

_End of architecture notes_
