"""艾丽妮 — generated from ArknightsGameData char_4009_irene.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4009_irene
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_irene() -> UnitState:
    return UnitState(
        name='艾丽妮',
        faction=Faction.ALLY,
        max_hp=2935,
        atk=701,
        defence=369,
        res=0.0,
        atk_interval=1.3,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=23,
        redeploy_cd=70.0,
    )
