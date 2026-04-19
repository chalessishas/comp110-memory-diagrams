"""Auto-discovering operator factory registry.

Pulls `make_*` functions from:
  - data/characters/*.py         (curated — stats + skills hand-authored)
  - data/characters/generated/*.py (akgd auto-generated — stats only)

Curated entries take precedence over generated ones.

Access:
    from data.characters.registry import get_operator, list_operators
    op = get_operator("svrash")
    all_keys = list_operators()
"""
from __future__ import annotations
import importlib
import pkgutil
from typing import Callable, Dict, List

from core.state.unit_state import UnitState


def _discover(subpackage: str) -> Dict[str, Callable[..., UnitState]]:
    """Find every `make_<handle>` callable in modules under `data.characters.<subpackage>`.

    Handle is derived from either the function name (e.g. `make_silverash` -> `silverash`)
    or the module name when the function signature is complex.
    """
    factories: Dict[str, Callable[..., UnitState]] = {}
    # Import the subpackage
    full_name = f"data.characters.{subpackage}" if subpackage else "data.characters"
    try:
        pkg = importlib.import_module(full_name)
    except ImportError:
        return factories

    for modinfo in pkgutil.iter_modules(pkg.__path__):
        if modinfo.ispkg:
            continue
        mod_name = modinfo.name
        if mod_name.startswith("_"):
            continue
        try:
            mod = importlib.import_module(f"{full_name}.{mod_name}")
        except Exception as e:
            print(f"[registry] failed to import {mod_name}: {e}")
            continue
        # Find make_<handle>
        for attr_name in dir(mod):
            if not attr_name.startswith("make_"):
                continue
            fn = getattr(mod, attr_name)
            if not callable(fn):
                continue
            handle = attr_name[5:].lower()   # strip "make_"
            factories.setdefault(handle, fn)
            # also register under the module filename (more predictable)
            factories.setdefault(mod_name.lower(), fn)
    return factories


# Generated first, curated overrides on top
_GENERATED = _discover("generated")
_CURATED = _discover("")          # data/characters/ root
_GENERATED.update(_CURATED)       # curated wins on conflicts
_REGISTRY = _GENERATED


def get_operator(handle: str) -> UnitState:
    """Build an operator by handle. Raises KeyError if unknown."""
    handle = handle.lower()
    if handle not in _REGISTRY:
        raise KeyError(
            f"Unknown operator {handle!r}. "
            f"Known: {len(_REGISTRY)} total. Use list_operators() to browse."
        )
    return _REGISTRY[handle]()


def list_operators() -> List[str]:
    """Return sorted list of known operator handles."""
    return sorted(_REGISTRY.keys())


def operator_count() -> int:
    return len(_REGISTRY)


def has_operator(handle: str) -> bool:
    return handle.lower() in _REGISTRY
