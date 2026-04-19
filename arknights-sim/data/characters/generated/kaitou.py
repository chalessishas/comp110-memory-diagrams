"""折光 — generated from ArknightsGameData char_499_kaitou.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_499_kaitou
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_kaitou() -> UnitState:
    return UnitState(
        name='折光',
        faction=Faction.ALLY,
        max_hp=1309,
        atk=643,
        defence=111,
        res=15.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.CASTER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=20,
        redeploy_cd=70.0,
    )
