"""阿消 — generated from ArknightsGameData char_277_sqrrel.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_277_sqrrel
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_sqrrel() -> UnitState:
    return UnitState(
        name='阿消',
        faction=Faction.ALLY,
        max_hp=1985,
        atk=615,
        defence=365,
        res=0.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.SPECIALIST,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=19,
        redeploy_cd=70.0,
    )
