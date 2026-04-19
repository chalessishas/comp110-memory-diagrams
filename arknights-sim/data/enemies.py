"""Enemy factories. Path is injected at spawn time (see stages/loader.py)."""
from __future__ import annotations
from typing import List, Tuple
from core.enemy import Enemy


def make_originium_slug(path: List[Tuple[int, int]] | None = None) -> Enemy:
    return Enemy(
        name="Originium Slug",
        max_hp=1300, atk=280, defence=0, res=0,
        atk_interval=1.5, attack_type="physical",
        path=path or [], speed=1.0,
    )


def make_arts_master(path: List[Tuple[int, int]] | None = None) -> Enemy:
    """Arts Master — magic-damage elite with moderate bulk.

    Loosely modelled on the canonical Arts Master stats: magic damage that
    bypasses DEF, slow cadence, enough HP to force skill usage on the
    attacker side.
    """
    return Enemy(
        name="Arts Master",
        max_hp=11000, atk=310, defence=100, res=10,
        atk_interval=3.0, attack_type="magic",
        path=path or [], speed=0.7,
    )
