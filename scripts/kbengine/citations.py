"""Citation resolution: which file a cited path names, across the libraries registered on this
machine (#252). An answer cites the file it rests on, by whatever path it walked; grading resolves
that to one file and compares files, never text. Stdlib only. Reads kbengine.registry and does not
extend it.

installed()                         {name: root} of the libraries registered and in state ok, read
                                    once per process (cache_clear() re-reads it).
declared(lib)                       the `domain:` a library's root INDEX.md declares, or None.
library_root(lib, name)             the root of the library called name: lib itself if that is the name
                                    it declares, else the registered one, else None.
expected_target(lib, expected)      (root, path within it) of a golden record's expected_file, which may
                                    be <library>:<path> for a file in another installed library.
candidates(lib, cited)              every file a cited path may name: library-relative (x.md),
                                    library-prefixed (<lib>/x.md), kb-rooted (kb/<lib>/x.md) or absolute.
resolves_to(lib, expected, cited)   whether any of the cited paths names the expected file.

It was a pure move out of scripts/grade-eval, which grade-routing, kb-telemetry and kb-eval-sample
loaded for it: its judgements are unchanged.
"""
import functools, pathlib, re

from . import registry


@functools.lru_cache(maxsize=None)
def installed():
    """{name: root} of the libraries registered on this machine (ADR-0014), read through
    kbengine.registry, the registry's one reader."""
    return registry.installed()


def declared(lib: pathlib.Path):
    """The name a library declares for itself, or None if it declares none it could be registered by."""
    return registry.declared_name(lib)


def library_root(lib: pathlib.Path, name: str):
    """The root of the library called `name`: the library being graded, if that is the name it
    declares, else the registered one, else None (not installed on this machine)."""
    lib = lib.resolve()
    return lib if declared(lib) == name else installed().get(name)


def expected_target(lib: pathlib.Path, expected: str):
    """(library root, path within it) of the file a golden record's expected_file names. A
    cross-root case may name a file in another installed library as <library>:<path> (issue
    #36); anything else is a path in the case's own library. The root is None when the named
    library is not installed on this machine."""
    m = re.fullmatch(r"([\w-]+):(.+)", expected)
    return (library_root(lib, m.group(1)), m.group(2)) if m else (lib.resolve(), expected)


def candidates(lib: pathlib.Path, cited: str):
    """Every file a cited path may name. An agent cites by whatever path it walked:
    library-relative (x.md), library-prefixed (<lib>/x.md), kb-rooted (kb/<lib>/x.md) or
    absolute. A library prefix resolves through the registry, wherever that library lives;
    the rest resolve against the library, its parent and its grandparent."""
    lib = lib.resolve()          # "." has no parent to anchor on until it is resolved
    p = pathlib.Path(cited)
    out = [a / p for a in (lib, lib.parent, lib.parent.parent)]
    parts = p.parts[1:] if p.parts[:1] == ("kb",) else p.parts
    if len(parts) > 1 and (root := library_root(lib, parts[0])):
        out.append(root.joinpath(*parts[1:]))
    return out


def resolves_to(lib: pathlib.Path, expected: str, cited) -> bool:
    """True if any cited path names the expected file. Each is RESOLVED and compared as a
    file — never matched as a suffix, which would let a same-named file in another library
    pass."""
    owner, rel = expected_target(lib, expected)
    if owner is None:
        return False
    want = (owner / rel).resolve()
    return any(f.resolve() == want for c in cited for f in candidates(lib, c))
