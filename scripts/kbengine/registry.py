"""The per-machine library registry, read once and the same way by every script that needs it
(ADR-0014, ADR-0020, #210). The registry is ~/.config/ai-kb/libraries in git-config format; the
kb-libraries script documents the format and the states and is the CLI over this module. Stdlib only.

entries()          [{name, path, origin, read_only, ref, state}] for every registered library, in
                   name order. Raises RuntimeError if the registry exists and git cannot read it.
installed()        {name: resolved path} for every library in state ok: the set that is served.
read_only(path)    the registry entry of the read-only library at path, or None. An unreadable
                   registry reads as no entry.
read_only_paths()  {resolved path} of every read-only library. Raises like entries().
refusal(tool, e)   the one wording for a writer that refuses a read-only library.
declared_name(lib) the `domain:` a library's root INDEX.md declares, if it can be a registered name.
state_of(name, p)  the state of one registered library.
"""
import pathlib, re, subprocess

from . import env, library

NAME = re.compile(r"[\w-]+")      # what a registered library may be called


def declared_name(lib: pathlib.Path):
    """The `domain:` a library's root INDEX.md declares in its frontmatter, if it is a name a
    library can be registered by, else None."""
    name = library.library(lib).name
    return name if name and NAME.fullmatch(name) else None


def contract_supported(path: pathlib.Path) -> bool:
    """False if the library's kb_contract is an unsupported major or unreadable (ADR-0016). True
    if this engine cannot read its own contract versions: that is an engine defect check-kb
    reports, not grounds to withhold every library."""
    status = library.library(path).contract
    return status is None or status[0] not in ("unsupported", "malformed")


def state_of(name: str, path: pathlib.Path) -> str:
    if not path.exists():
        return "missing"
    if not (path / "INDEX.md").is_file():
        return "not-a-library"
    if declared_name(path) != name:
        return "name-mismatch"
    return "ok" if contract_supported(path) else "unsupported-contract"


def entries():
    """[{name, path, origin, read_only, ref, state}] for every registered library, in name order."""
    registry = env.registry_path()
    if not registry.is_file():
        return []
    r = subprocess.run(["git", "config", "--file", str(registry), "--null", "--list"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"cannot read {registry}: {r.stderr.strip()}")
    libs = {}
    for rec in r.stdout.split("\0"):
        key, _, value = rec.partition("\n")
        if not key.startswith("library.") or key.count(".") < 2:
            continue
        name, field = key[len("library."):].rsplit(".", 1)
        libs.setdefault(name, {})[field] = value
    out = []
    for name in sorted(libs):
        if "path" not in libs[name]:
            continue
        path = pathlib.Path(libs[name]["path"])
        out.append({"name": name, "path": path, "origin": libs[name].get("origin", ""),
                    "read_only": libs[name].get("readonly", "").lower() == "true",
                    "ref": libs[name].get("ref", ""), "state": state_of(name, path)})
    return out


def installed():
    """{name: resolved path} for every library in state ok: the set that is served."""
    return {e["name"]: e["path"].resolve() for e in entries() if e["state"] == "ok"}


def read_only_paths() -> set:
    """{resolved path} of every library registered read-only (ADR-0020), whatever its state."""
    return {e["path"].resolve() for e in entries() if e["read_only"]}


def read_only(path) -> dict:
    """The registry entry of the read-only library at path, or None (ADR-0020). Every script that
    writes into a library asks this first. An unreadable registry reads as no entry: the writer then
    behaves as it did before read-only libraries existed, and session start names the registry."""
    try:
        here = pathlib.Path(path).resolve()
        return next((e for e in entries() if e["read_only"] and e["path"].resolve() == here), None)
    except (RuntimeError, OSError):
        return None


def refusal(tool: str, e: dict) -> str:
    """One wording for every writer that refuses a read-only library."""
    where = e["origin"] or "its publisher"
    return (f"{tool}: {e['name']} is registered read-only on this machine, a consumer's copy: it is "
            f"not curated here (ADR-0020). File what you found with {where}. To curate it here: "
            f"kb-library add {e['path']}")
