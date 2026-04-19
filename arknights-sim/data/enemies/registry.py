"""Auto-discovering enemy factory registry.

Pulls `make_*` callables from:
  - data/enemies/*.py            (curated — named units, special behaviors)
  - data/enemies/generated/*.py  (akgd auto-generated — 1859 enemies)

Curated entries win on conflict.
"""
from __future__ import annotations
import importlib
import pkgutil
from typing import Callable, Dict, List, Tuple

from core.state.unit_state import UnitState


EnemyFactory = Callable[..., UnitState]


def _discover(subpackage: str) -> Dict[str, EnemyFactory]:
    factories: Dict[str, EnemyFactory] = {}
    full_name = f"data.enemies.{subpackage}" if subpackage else "data.enemies"
    try:
        pkg = importlib.import_module(full_name)
    except ImportError:
        return factories

    for modinfo in pkgutil.iter_modules(pkg.__path__):
        if modinfo.ispkg:
            continue
        if modinfo.name.startswith("_"):
            continue
        try:
            mod = importlib.import_module(f"{full_name}.{modinfo.name}")
        except Exception as e:
            print(f"[enemy_registry] failed to import {modinfo.name}: {e}")
            continue
        for attr_name in dir(mod):
            if not attr_name.startswith("make_"):
                continue
            fn = getattr(mod, attr_name)
            if not callable(fn):
                continue
            handle = attr_name[5:].lower()
            factories.setdefault(handle, fn)
            factories.setdefault(modinfo.name.lower(), fn)
    return factories


_GENERATED = _discover("generated")
_CURATED = _discover("")
_GENERATED.update(_CURATED)
_REGISTRY = _GENERATED


def get_enemy(handle: str, path: List[Tuple[int, int]] | None = None) -> UnitState:
    handle = handle.lower()
    if handle not in _REGISTRY:
        raise KeyError(f"Unknown enemy {handle!r}. Registry has {len(_REGISTRY)} entries.")
    fn = _REGISTRY[handle]
    try:
        return fn(path=path) if path is not None else fn()
    except TypeError:
        # Some factories don't take path
        return fn()


def list_enemies() -> List[str]:
    return sorted(_REGISTRY.keys())


def enemy_count() -> int:
    return len(_REGISTRY)


def has_enemy(handle: str) -> bool:
    return handle.lower() in _REGISTRY
