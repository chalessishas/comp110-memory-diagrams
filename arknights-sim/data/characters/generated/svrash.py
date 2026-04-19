"""银灰 — generated from ArknightsGameData char_172_svrash.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_172_svrash
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_svrash() -> UnitState:
    return UnitState(
        name='银灰',
        faction=Faction.ALLY,
        max_hp=2560,
        atk=763,
        defence=447,
        res=10.0,
        atk_interval=1.3,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=0,
        redeploy_cd=70.0,
    )
