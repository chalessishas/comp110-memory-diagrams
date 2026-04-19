"""米格鲁 — generated from ArknightsGameData char_122_beagle.
Source: E1 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_122_beagle
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_beagle() -> UnitState:
    return UnitState(
        name='米格鲁',
        faction=Faction.ALLY,
        max_hp=2035,
        atk=295,
        defence=550,
        res=0.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.DEFENDER,
        attack_type=AttackType.PHYSICAL,
        block=3,
        cost=18,
        redeploy_cd=70.0,
    )
