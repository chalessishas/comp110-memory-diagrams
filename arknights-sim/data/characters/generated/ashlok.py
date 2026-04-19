"""灰毫 — generated from ArknightsGameData char_431_ashlok.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_431_ashlok
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_ashlok() -> UnitState:
    return UnitState(
        name='灰毫',
        faction=Faction.ALLY,
        max_hp=3207,
        atk=915,
        defence=591,
        res=0.0,
        atk_interval=2.8,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.DEFENDER,
        attack_type=AttackType.PHYSICAL,
        block=3,
        cost=27,
        redeploy_cd=70.0,
    )
