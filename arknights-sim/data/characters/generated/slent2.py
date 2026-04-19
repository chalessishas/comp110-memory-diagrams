"""淬羽赫默 — generated from ArknightsGameData char_1031_slent2.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_1031_slent2
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_slent2() -> UnitState:
    return UnitState(
        name='淬羽赫默',
        faction=Faction.ALLY,
        max_hp=2277,
        atk=522,
        defence=184,
        res=25.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SUPPORTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=15,
        redeploy_cd=80.0,
    )
