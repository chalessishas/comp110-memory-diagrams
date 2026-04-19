"""翎羽 — generated from ArknightsGameData char_192_falco.
Source: E1 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_192_falco
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_falco() -> UnitState:
    return UnitState(
        name='翎羽',
        faction=Faction.ALLY,
        max_hp=1226,
        atk=495,
        defence=279,
        res=0.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.VANGUARD,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=10,
        redeploy_cd=70.0,
    )
