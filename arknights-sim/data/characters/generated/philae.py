"""菲莱 — generated from ArknightsGameData char_4148_philae.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4148_philae
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_philae() -> UnitState:
    return UnitState(
        name='菲莱',
        faction=Faction.ALLY,
        max_hp=3227,
        atk=643,
        defence=584,
        res=10.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.DEFENDER,
        attack_type=AttackType.PHYSICAL,
        block=3,
        cost=25,
        redeploy_cd=70.0,
    )
