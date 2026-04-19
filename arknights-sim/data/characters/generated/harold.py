"""哈洛德 — generated from ArknightsGameData char_4114_harold.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4114_harold
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_harold() -> UnitState:
    return UnitState(
        name='哈洛德',
        faction=Faction.ALLY,
        max_hp=1550,
        atk=420,
        defence=100,
        res=10.0,
        atk_interval=2.85,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.MEDIC,
        attack_type=AttackType.HEAL,
        block=1,
        cost=17,
        redeploy_cd=80.0,
    )
