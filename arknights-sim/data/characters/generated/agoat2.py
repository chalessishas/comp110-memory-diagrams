"""纯烬艾雅法拉 — generated from ArknightsGameData char_1016_agoat2.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_1016_agoat2
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_agoat2() -> UnitState:
    return UnitState(
        name='纯烬艾雅法拉',
        faction=Faction.ALLY,
        max_hp=1639,
        atk=469,
        defence=109,
        res=10.0,
        atk_interval=2.85,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.MEDIC,
        attack_type=AttackType.HEAL,
        block=1,
        cost=16,
        redeploy_cd=70.0,
    )
