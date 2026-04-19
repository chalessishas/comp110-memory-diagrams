"""风笛 — generated from ArknightsGameData char_222_bpipe.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_222_bpipe
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_bpipe() -> UnitState:
    return UnitState(
        name='风笛',
        faction=Faction.ALLY,
        max_hp=2484,
        atk=671,
        defence=382,
        res=0.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.VANGUARD,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=13,
        redeploy_cd=70.0,
    )
