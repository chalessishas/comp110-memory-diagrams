"""泡普卡 — generated from ArknightsGameData char_281_popka.
Source: E1 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_281_popka
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_popka() -> UnitState:
    return UnitState(
        name='泡普卡',
        faction=Faction.ALLY,
        max_hp=1858,
        atk=545,
        defence=245,
        res=0.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=19,
        redeploy_cd=70.0,
    )
