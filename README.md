# Distrohopper

Declarative, cross-distro OS bootstrapper for people who like to hop between Linux distributions but keep the same working environment.

* Write **one Python file** that lists the apps you need and how their config files must look after the run.
* Run `pyinfra` against any supported host (Ubuntu, Debian, Fedora; more coming) – packages are installed, PPAs/repos are added, dot-files are patched, even arbitrary Python code can be executed remotely.

The project is a thin, opinionated wrapper around [pyinfra](https://pyinfra.dev) that provides:

1. Simple **Python domain syntax** instead of raw pyinfra inventory + operations files.
2. **Multi-OS abstractions** – choose `Apt`, `Dnf`, `Snap`, … once and let the library pick the right operations on each host.
3. High-level helpers for **editing structured text files** (JSON/YAML/INI/XML/Plist) *idempotently*.
4. A safe wrapper to **run short Python snippets/functions** on the remote machine when you really need imperative logic.

> **Status** – experimental/prototype.  Works on Ubuntu 22.04, Debian 12 and Fedora 40 when executed as root.  Breaking changes are expected while API is being stabilised.

---

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# create hosts.pyinfra inventory, e.g. `test_inventory.py` or use one of yours
pyinfra @local apps_example.py  # dry-run
pyinfra @local apps_example.py --apply  # apply changes
```

See `apps_example.py` for a self-documented example.

---

## Documentation

* `docs/api.md` – full end-user API reference with examples.
* `docs/arch.md` – implementation notes and developer roadmap.

---

## Contributing

1. Fork, hack, run `pytest`, send PR.
2. For bigger ideas check `docs/arch.md` and open an issue first.

---

## License

MIT – see `LICENSE` file (to be added).
